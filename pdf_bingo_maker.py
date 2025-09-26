from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import io
import os

def create_image_with_custom_text(template_path, custom_texts, font_path="arial.ttf"):
    """
    Create an image with custom text in the grid cells
    
    Args:
        template_path: Path to the template image
        custom_texts: List of 48 text items (8 main cells × 6 inner cells each)
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
    font = ImageFont.truetype(font_path, font_size)
    
    # Track text index
    text_idx = 0
    
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
        for inner_idx in range(6):  # 2 rows × 3 cols = 6 cells
            inner_col = inner_idx % inner_cols
            inner_row = inner_idx // inner_cols
            
            # Get text for this cell
            if text_idx < len(custom_texts):
                inner_text = custom_texts[text_idx]
            else:
                inner_text = f"R{inner_row+1}C{inner_col+1}"
            text_idx += 1
            
            # Calculate position of this inner cell
            inner_cell_x0 = inner_x0 + inner_col * inner_cell_width
            inner_cell_y0 = inner_y0 + inner_row * inner_cell_height
            inner_cell_x1 = inner_cell_x0 + inner_cell_width
            inner_cell_y1 = inner_cell_y0 + inner_cell_height
            
            # Find the largest font size that fits
            max_font_size = 10
            max_possible_size = min(inner_cell_width, inner_cell_height) // 2
            for size in range(10, max_possible_size, 2):
                try:
                    test_font = ImageFont.truetype(font_path, size)
                    bbox = test_font.getbbox(inner_text)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    if text_width < inner_cell_width * 0.8 and text_height < inner_cell_height * 0.8:
                        max_font_size = size
                    else:
                        break
                except:
                    break
            
            # Draw the text
            try:
                final_font = ImageFont.truetype(font_path, max_font_size)
            except:
                # Fallback to default font if arial.ttf is not found
                final_font = ImageFont.load_default()
            
            bbox = final_font.getbbox(inner_text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = inner_cell_x0 + (inner_cell_width - text_width) // 2
            text_y = inner_cell_y0 + (inner_cell_height - text_height) // 2
            
            draw.text((text_x, text_y), inner_text, font=final_font, fill=(255, 255, 255))
    
    return image

def create_pdf_with_multiple_cards(template_path, cards_data, output_pdf_path, page_size=A4):
    """
    Create a PDF with multiple bingo cards
    
    Args:
        template_path: Path to the template image
        cards_data: List of dictionaries, each with 'title' and 'texts' (48 items)
        output_pdf_path: Path for the output PDF
        page_size: Page size for the PDF
    """
    c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    page_width, page_height = page_size
    
    for i, card_data in enumerate(cards_data):
        card_title = card_data.get('title', f'Bingo Card {i + 1}')
        card_texts = card_data.get('texts', [])
        
        # Create image with current text variation
        image = create_image_with_custom_text(template_path, card_texts)
        
        # Convert PIL image to bytes for reportlab
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Calculate image dimensions to fit on page while maintaining aspect ratio
        img_width, img_height = image.size
        aspect_ratio = img_width / img_height
        
        # Leave some margin
        max_width = page_width - 100
        max_height = page_height - 120  # Extra space for title
        
        if max_width / aspect_ratio <= max_height:
            scaled_width = max_width
            scaled_height = max_width / aspect_ratio
        else:
            scaled_height = max_height
            scaled_width = max_height * aspect_ratio
        
        # Center the image on the page
        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2 - 20  # Offset for title
        
        # Add the image to the PDF
        c.drawImage(ImageReader(img_buffer), x, y, width=scaled_width, height=scaled_height)
        
        # Add page title
        c.setFont("Helvetica-Bold", 20)
        title_width = c.stringWidth(card_title, "Helvetica-Bold", 20)
        title_x = (page_width - title_width) / 2
        c.drawString(title_x, page_height - 40, card_title)
        
        # Start a new page (except for the last image)
        if i < len(cards_data) - 1:
            c.showPage()
    
    c.save()
    print(f"PDF created successfully: {output_pdf_path}")

# Example usage
if __name__ == "__main__":
    template_path = "template.jpg"
    
    # Define your bingo cards here
    # Each card needs exactly 48 text items (8 main cells × 6 inner cells each)
    bingo_cards = [
        {
            'title': 'Musical Genres Bingo',
            'texts': [
                # Main cell 1 (6 texts)
                "Rock", "Pop", "Jazz", "Blues", "Folk", "Punk",
                # Main cell 2 (6 texts)
                "Hip-Hop", "R&B", "Soul", "Funk", "Disco", "House",
                # Main cell 3 (6 texts)
                "Metal", "Death", "Black", "Power", "Prog", "Doom",
                # Main cell 4 (6 texts)
                "Country", "Western", "Bluegrass", "Honky", "Alt", "New",
                # Main cell 5 (6 texts)
                "Electronic", "Techno", "Trance", "Dubstep", "Ambient", "IDM",
                # Main cell 6 (6 texts)
                "Classical", "Baroque", "Romantic", "Modern", "Opera", "Chamber",
                # Main cell 7 (6 texts)
                "World", "Latin", "African", "Asian", "Celtic", "Reggae",
                # Main cell 8 (6 texts)
                "Alternative", "Indie", "Grunge", "Post-Rock", "Shoegaze", "Emo"
            ]
        },
        {
            'title': 'Musical Instruments Bingo',
            'texts': [
                "Guitar", "Bass", "Violin", "Cello", "Piano", "Organ",
                "Drums", "Cymbals", "Snare", "Kick", "Hi-Hat", "Tom",
                "Trumpet", "Trombone", "F.Horn", "Tuba", "Cornet", "Flugelhorn",
                "Flute", "Clarinet", "Oboe", "Bassoon", "Piccolo", "Recorder",
                "Sax", "Alto", "Tenor", "Soprano", "Baritone", "Bass",
                "Harmonica", "Accordion", "Banjo", "Mandolin", "Ukulele", "Harp",
                "Synth", "Keyboard", "Sampler", "Sequencer", "DrumMachine", "MIDI",
                "Vocals", "Soprano", "Alto", "Tenor", "Bass", "Falsetto"
            ]
        },
        {
            'title': 'Famous Artists Bingo',
            'texts': [
                "Beatles", "John", "Paul", "George", "Ringo", "Liverpool",
                "Elvis", "Presley", "King", "Rock", "Roll", "Memphis",
                "Mozart", "Wolfgang", "Amadeus", "Classical", "Composer", "Austria",
                "Miles", "Davis", "Jazz", "Trumpet", "Cool", "Bebop",
                "Bob", "Dylan", "Folk", "Nobel", "Harmonica", "Minnesota",
                "Madonna", "Pop", "Queen", "Material", "Girl", "Detroit",
                "Hendrix", "Jimi", "Guitar", "Purple", "Haze", "Seattle",
                "Beethoven", "Ludwig", "Symphony", "Deaf", "German", "Composer"
            ]
        }
    ]
    
    # Create the PDF
    output_pdf = "musical_bingo_cards.pdf"
    create_pdf_with_multiple_cards(template_path, bingo_cards, output_pdf)
    
    # Try to open the PDF
    try:
        os.startfile(output_pdf)
        print("PDF opened successfully!")
    except Exception as e:
        print(f"Could not open PDF automatically: {e}")
        print(f"You can manually open: {output_pdf}")
