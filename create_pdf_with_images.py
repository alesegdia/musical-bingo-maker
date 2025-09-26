from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import io
import os

def create_image_with_text(template_path, cell_texts_list, font_path="JandaManateeSolid.ttf"):
    """
    Create an image with custom text in the grid cells
    
    Args:
        template_path: Path to the template image
        cell_texts_list: List of lists, where each inner list contains text for each inner cell
        font_path: Path to the font file
    
    Returns:
        PIL Image object
    """
    # Load the image
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    
    # Define grid parameters
    cols = 2
    rows = 4
    
    # Get image size
    img_width, img_height = image.size
    cell_width = img_width // cols
    cell_height = img_height // rows
    
    # Load font
    font_size = 48
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        # Fallback to default font if truetype font fails
        font = ImageFont.load_default()
    
    # Draw grid and text for each main cell
    for main_cell_idx in range(cols * rows):
        col = main_cell_idx % cols
        row = main_cell_idx // cols
        x0 = col * cell_width
        y0 = row * cell_height
        
        # Draw the cell bounding box with thick green lines
        draw.rectangle([x0, y0, x0 + cell_width, y0 + cell_height], outline=(0, 255, 0), width=10)
        
        # Blue inner rectangle parameters
        blue_x_offset = 45
        blue_y_offset = 140
        blue_width = 650
        blue_height = 330
        
        inner_x0 = x0 + blue_x_offset
        inner_y0 = y0 + blue_y_offset
        inner_x1 = inner_x0 + blue_width
        inner_y1 = inner_y0 + blue_height
        draw.rectangle([inner_x0, inner_y0, inner_x1, inner_y1], outline=(0, 0, 255), width=6)
        
        # Inner grid parameters
        inner_cols = 3
        inner_rows = 2
        inner_cell_width = (inner_x1 - inner_x0) // inner_cols
        inner_cell_height = (inner_y1 - inner_y0) // inner_rows
        
        # Draw vertical red lines
        for i in range(1, inner_cols):
            x = inner_x0 + i * inner_cell_width
            draw.line([(x, inner_y0), (x, inner_y1)], fill=(255, 0, 0), width=6)
        
        # Draw horizontal red lines
        for j in range(1, inner_rows):
            y = inner_y0 + j * inner_cell_height
            draw.line([(inner_x0, y), (inner_x1, y)], fill=(255, 0, 0), width=6)
        
        # Add text to each inner cell
        if main_cell_idx < len(cell_texts_list):
            inner_cell_texts = cell_texts_list[main_cell_idx]
        else:
            inner_cell_texts = [f"R{r+1}C{c+1}" for r in range(inner_rows) for c in range(inner_cols)]
        
        for inner_idx, inner_text in enumerate(inner_cell_texts[:6]):  # Limit to 6 cells
            inner_col = inner_idx % inner_cols
            inner_row = inner_idx // inner_cols
            
            # Calculate position of this inner cell
            inner_cell_x0 = inner_x0 + inner_col * inner_cell_width
            inner_cell_y0 = inner_y0 + inner_row * inner_cell_height
            inner_cell_x1 = inner_cell_x0 + inner_cell_width
            inner_cell_y1 = inner_cell_y0 + inner_cell_height
            
            # Function to wrap text to fit in cell width
            def wrap_text(text, font, max_width):
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    bbox = font.getbbox(test_line)
                    test_width = bbox[2] - bbox[0]
                    
                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                            current_line = word
                        else:
                            # Single word is too long, add it anyway
                            lines.append(word)
                
                if current_line:
                    lines.append(current_line)
                
                return lines
            
            # Find the largest font size that fits with text wrapping
            max_font_size = 10
            max_possible_size = min(inner_cell_width, inner_cell_height) // 4  # More conservative for multiline
            max_possible_size = min(max_possible_size, 35)  # Hard limit at 35px for better fit
            
            best_font = None
            best_lines = []
            
            # Start with a reasonable size and work our way up
            for size in range(8, max_possible_size + 1, 1):
                try:
                    test_font = ImageFont.truetype(font_path, size)
                except:
                    test_font = ImageFont.load_default()
                
                try:
                    # Try wrapping text with this font size
                    wrapped_lines = wrap_text(inner_text, test_font, inner_cell_width * 0.9)
                    
                    # Calculate total text height
                    if wrapped_lines:
                        line_bbox = test_font.getbbox("Ay")  # Use a sample for line height
                        line_height = line_bbox[3] - line_bbox[1]
                        total_text_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * (line_height * 0.2)  # Add some line spacing
                        
                        # Check if all lines fit vertically
                        if total_text_height <= inner_cell_height * 0.9:
                            max_font_size = size
                            best_font = test_font
                            best_lines = wrapped_lines
                        else:
                            break
                    else:
                        break
                except:
                    # If wrapping fails, stick with current size
                    break
            
            # Draw the wrapped text with proper font fallback
            if not best_font:
                try:
                    best_font = ImageFont.truetype(font_path, max_font_size)
                except:
                    best_font = ImageFont.load_default()
                best_lines = wrap_text(inner_text, best_font, inner_cell_width * 0.9)
            
            # Draw each line of text
            if best_lines:
                line_bbox = best_font.getbbox("Ay")  # Use sample for consistent line height
                line_height = line_bbox[3] - line_bbox[1]
                line_spacing = line_height * 0.2
                total_text_height = len(best_lines) * line_height + (len(best_lines) - 1) * line_spacing
                
                # Start from the top of the centered text block
                start_y = inner_cell_y0 + (inner_cell_height - total_text_height) // 2
                
                for line_idx, line in enumerate(best_lines):
                    line_bbox = best_font.getbbox(line)
                    line_width = line_bbox[2] - line_bbox[0]
                    
                    # Center each line horizontally
                    text_x = inner_cell_x0 + (inner_cell_width - line_width) // 2
                    text_y = start_y + line_idx * (line_height + line_spacing)
                    
                    draw.text((text_x, text_y), line, font=best_font, fill=(255, 255, 255))
    
    return image

def create_pdf_with_images(template_path, text_variations, output_pdf_path, page_size=A4):
    """
    Create a PDF with multiple images, each with different text
    
    Args:
        template_path: Path to the template image
        text_variations: List of text variations, where each variation is a list of lists
                        (one list per main cell, containing text for inner cells)
        output_pdf_path: Path for the output PDF
        page_size: Page size for the PDF (default A4)
    """
    c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    page_width, page_height = page_size
    
    for i, cell_texts_list in enumerate(text_variations):
        print(f"Processing page {i+1}/{len(text_variations)}...")
        # Create image with current text variation
        image = create_image_with_text(template_path, cell_texts_list)
        
        # Convert PIL image to bytes for reportlab
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Calculate image dimensions to fit on page while maintaining aspect ratio
        img_width, img_height = image.size
        aspect_ratio = img_width / img_height
        
        # Leave minimal margin (2 points on each side for printer safety)
        max_width = page_width - 4
        max_height = page_height - 4
        
        if max_width / aspect_ratio <= max_height:
            # Width is the limiting factor
            scaled_width = max_width
            scaled_height = max_width / aspect_ratio
        else:
            # Height is the limiting factor
            scaled_height = max_height
            scaled_width = max_height * aspect_ratio
        
        # Center the image on the page
        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2
        
        # Add the image to the PDF
        c.drawImage(ImageReader(img_buffer), x, y, width=scaled_width, height=scaled_height)
        
        # Add page title in bottom right corner to avoid interfering with the image
        c.setFont("Helvetica-Bold", 12)
        title_text = f"Page {i + 1}"
        title_width = c.stringWidth(title_text, "Helvetica-Bold", 12)
        c.drawString(page_width - title_width - 10, 10, title_text)
        
        # Start a new page (except for the last image)
        if i < len(text_variations) - 1:
            c.showPage()
    
    c.save()
    print(f"PDF created successfully: {output_pdf_path}")

# Example usage
if __name__ == "__main__":
    template_path = "template.jpg"

    canciones = [
        "La Cucaracha",
        "La Mayonesa",
        "El anillo",
        "Despacito",
        "Gasolina",
        "Danza Kuduro",
        "Bailando",
        "Súbeme la radio",
        "Felices los 4",
        "Hawái",
        "Paquito el Chocolatero",
        "Que viva España",
        "Eva María",
        "Un rayo de sol",
        "La chica yeyé",
        "Sarandonga",
        "El tractor amarillo",
        "Libre",
        "Corazón partío",
        "Colgando en tus manos",
        "El tiburón",
        "Carnaval, carnaval",
        "La barbacoa",
        "Cuentan las lenguas antiguas",
        "Macarena",
        "Aserejé",
        "Waka Waka",
        "Hips don’t lie",
        "Oma yo viazé un corrá",
        "Livin’ la vida loca",
        "Ese toro enamorao de la luna",
        "En qué estrella estará",
        "Yo perreo sola",
        "La gasolina",
        "Tengo el corazón contento",
        "Cuando zarpa el amor",
        "Sueño contigo, que más dado",
        "La bicicleta",
        "Robarte un beso",
        "Qué bonito",
        "Como yo te amo",
        "Pájaros de barro",
        "La flaca",
        "Lobo hombre en París",
        "Chiquilla",
        "La Cucaracha",
        "La Mayonesa",
        "El anillo",
        "Despacito",
        "Gasolina",
        "Danza Kuduro",
        "Bailando",
        "Súbeme la radio",
        "Felices los 4",
        "Hawái",
        "Paquito el Chocolatero",
        "Que viva España",
        "Eva María",
        "Un rayo de sol",
        "La chica yeyé",
        "Sarandonga",
        "El tractor amarillo",
        "Libre",
        "Corazón partío",
        "Colgando en tus manos",
        "El tiburón",
        "Carnaval, carnaval",
        "La barbacoa",
        "Cuentan las lenguas antiguas",
        "Macarena",
        "Aserejé",
        "Waka Waka",
        "Hips don’t lie",
        "Oma yo viazé un corrá",
        "Livin’ la vida loca",
        "Ese toro enamorao de la luna",
        "En qué estrella estará",
        "Yo perreo sola",
        "La gasolina",
        "Tengo el corazón contento",
        "Cuando zarpa el amor",
        "Sueño contigo, que más dado",
        "La bicicleta",
        "Robarte un beso",
        "Qué bonito",
        "Como yo te amo",
        "Pájaros de barro",
        "La flaca",
        "Lobo hombre en París",
        "Chiquilla",
        "La Cucaracha",
        "La Mayonesa",
        "El anillo",
        "Despacito",
        "Gasolina",
        "Danza Kuduro",
        "Bailando",
        "Súbeme la radio",
        "Felices los 4",
        "Hawái",
        "Paquito el Chocolatero",
        "Que viva España",
        "Eva María",
        "Un rayo de sol",
        "La chica yeyé",
        "Sarandonga",
        "El tractor amarillo",
        "Libre",
        "Corazón partío",
        "Colgando en tus manos",
        "El tiburón",
        "Carnaval, carnaval",
        "La barbacoa",
        "Cuentan las lenguas antiguas",
        "Macarena",
        "Aserejé",
        "Waka Waka",
        "Hips don’t lie",
        "Oma yo viazé un corrá",
        "Livin’ la vida loca",
        "Ese toro enamorao de la luna",
        "En qué estrella estará",
        "Yo perreo sola",
        "La gasolina",
        "Tengo el corazón contento",
        "Cuando zarpa el amor",
        "Sueño contigo, que más dado",
        "La bicicleta",
        "Robarte un beso",
        "Qué bonito",
        "Como yo te amo",
        "Pájaros de barro",
        "La flaca",
        "Lobo hombre en París",
        "Chiquilla",
    ]

    canciones_ganadoras = [
        "Baby shark",
        "Tengo que impedir esa boda",
        "BSO El padrino",
        "Ay mama!",
        "El taxi",
        "La de tu hermana"
    ]

    num_sheets = 15

    # Generate text variations for bingo cards
    import random
    text_variations = []
    
    # Generate pages of bingo cards
    for page_num in range(1, num_sheets + 1):
        # Each page contains 8 bingo cards (8 main cells, each with 6 songs)
        page_cards = []
        
        if page_num == 1:
            # First page: ensure one card contains ALL canciones_ganadoras (winning card)
            print(f"Generating Page {page_num} with WINNING CARD...")
            
            # First card on the page is the winning card
            winning_card_songs = canciones_ganadoras.copy()
            page_cards.append(winning_card_songs)
            
            # Generate 7 more cards for this page with random songs
            for card_idx in range(7):
                all_available = canciones + canciones_ganadoras
                card_songs = random.choices(all_available, k=6)
                page_cards.append(card_songs)
            
            print(f"Page {page_num}: Card 1 (WINNING) contains all canciones_ganadoras: {canciones_ganadoras}")
            
        else:
            # Other pages: generate 8 random cards
            print(f"Generating Page {page_num}...")
            
            for card_idx in range(8):
                all_available = canciones + canciones_ganadoras
                card_songs = random.choices(all_available, k=6)
                page_cards.append(card_songs)
        
        # Add this page to text_variations
        text_variations.append(page_cards)
        
        # Check which canciones_ganadoras are in each card of this page
        for card_idx, card_songs in enumerate(page_cards):
            ganadoras_in_card = [song for song in canciones_ganadoras if song in card_songs]
            if ganadoras_in_card:
                print(f"Page {page_num}, Card {card_idx + 1} contains {len(ganadoras_in_card)} canciones_ganadoras: {ganadoras_in_card}")
    
    # Create the PDF
    output_pdf = "musical_bingo_cards.pdf"
    create_pdf_with_images(template_path, text_variations, output_pdf)
    
    # Try to open the PDF
    try:
        os.startfile(output_pdf)
    except Exception as e:
        print(f"Could not open PDF automatically: {e}")
