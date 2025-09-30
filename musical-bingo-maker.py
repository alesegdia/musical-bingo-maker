from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import io
import os

# Boolean variable to control colored lines and page text
SHOW_LINES_AND_PAGE_TEXT = False

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
        
        # Draw the cell bounding box with thick green lines (only if enabled)
        if SHOW_LINES_AND_PAGE_TEXT:
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
        
        # Draw blue rectangle outline (only if enabled)
        if SHOW_LINES_AND_PAGE_TEXT:
            draw.rectangle([inner_x0, inner_y0, inner_x1, inner_y1], outline=(0, 0, 255), width=6)
        
        # Inner grid parameters
        inner_cols = 3
        inner_rows = 2
        inner_cell_width = (inner_x1 - inner_x0) // inner_cols
        inner_cell_height = (inner_y1 - inner_y0) // inner_rows
        
        # Draw vertical red lines (only if enabled)
        if SHOW_LINES_AND_PAGE_TEXT:
            for i in range(1, inner_cols):
                x = inner_x0 + i * inner_cell_width
                draw.line([(x, inner_y0), (x, inner_y1)], fill=(255, 0, 0), width=6)
        
        # Draw horizontal red lines (only if enabled)
        if SHOW_LINES_AND_PAGE_TEXT:
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
        
        # Add page title in bottom right corner (only if enabled)
        if SHOW_LINES_AND_PAGE_TEXT:
            c.setFont("Helvetica-Bold", 12)
            title_text = f"Page {i + 1}"
            title_width = c.stringWidth(title_text, "Helvetica-Bold", 12)
            c.drawString(page_width - title_width - 10, 10, title_text)
        
        # Start a new page (except for the last image)
        if i < len(text_variations) - 1:
            c.showPage()
    
    c.save()
    print(f"PDF created successfully: {output_pdf_path}")


def check_for_duplicate_cards(text_variations):
    """
    Comprehensive function to check for duplicate bingo cards across all pages.
    Two cards are considered duplicates if they contain the same songs, regardless of order.
    
    Args:
        text_variations: List of pages, where each page is a list of cards,
                        and each card is a list of songs
    """
    print(f"\n=== COMPREHENSIVE DUPLICATE CARD ANALYSIS ===")
    
    # Collect all cards with their location information
    all_cards = []
    total_cards = 0
    
    for page_idx, page in enumerate(text_variations):
        for card_idx, card_songs in enumerate(page):
            # Create a normalized signature (sorted set of songs)
            card_signature = tuple(sorted(set(card_songs)))  # Use set to handle any internal duplicates within a card
            card_info = {
                'signature': card_signature,
                'songs': card_songs,
                'page': page_idx + 1,
                'card': card_idx + 1,
                'location': f"Page {page_idx + 1}, Card {card_idx + 1}"
            }
            all_cards.append(card_info)
            total_cards += 1
    
    print(f"Total cards analyzed: {total_cards}")
    
    # Group cards by their signature to find duplicates
    signature_groups = {}
    for card_info in all_cards:
        signature = card_info['signature']
        if signature not in signature_groups:
            signature_groups[signature] = []
        signature_groups[signature].append(card_info)
    
    # Find duplicates
    duplicate_groups = {sig: cards for sig, cards in signature_groups.items() if len(cards) > 1}
    unique_cards = len(signature_groups)
    
    print(f"Unique card combinations: {unique_cards}")
    print(f"Duplicate groups found: {len(duplicate_groups)}")
    
    if duplicate_groups:
        print(f"\n⚠️ WARNING: Found {len(duplicate_groups)} sets of duplicate cards:")
        print(f"{'='*60}")
        
        duplicate_count = 0
        for group_idx, (signature, duplicate_cards) in enumerate(duplicate_groups.items(), 1):
            duplicate_count += len(duplicate_cards)
            print(f"\nDuplicate Group #{group_idx}:")
            print(f"  Songs: {list(signature)}")
            print(f"  Found in {len(duplicate_cards)} locations:")
            
            for card_info in duplicate_cards:
                print(f"    - {card_info['location']}")
        
        print(f"\n{'='*60}")
        print(f"Summary: {duplicate_count} total cards are duplicates")
        print(f"Affected cards: {duplicate_count} out of {total_cards} ({duplicate_count/total_cards*100:.1f}%)")
        
        # Provide recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   • Increase song variety in your song pools")
        print(f"   • Reduce the number of cards if song pool is limited")
        print(f"   • Ensure the card generation algorithm creates more unique combinations")
        
    else:
        print(f"\n✅ SUCCESS: All {total_cards} cards are unique!")
        print(f"   No duplicate cards found across all pages.")
    
    # Additional statistics
    print(f"\n📊 DETAILED STATISTICS:")
    
    # Song frequency analysis
    song_usage = {}
    total_song_slots = 0
    
    for card_info in all_cards:
        for song in card_info['songs']:
            song_usage[song] = song_usage.get(song, 0) + 1
            total_song_slots += 1
    
    most_used_songs = sorted(song_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    least_used_songs = sorted(song_usage.items(), key=lambda x: x[1])[:5]
    
    print(f"   • Total song slots across all cards: {total_song_slots}")
    print(f"   • Different songs used: {len(song_usage)}")
    print(f"   • Average uses per song: {total_song_slots/len(song_usage):.1f}")
    
    print(f"\n   Most frequently used songs:")
    for song, count in most_used_songs:
        percentage = (count / total_song_slots) * 100
        print(f"     - '{song}': {count} times ({percentage:.1f}%)")
    
    print(f"\n   Least frequently used songs:")
    for song, count in least_used_songs:
        percentage = (count / total_song_slots) * 100
        print(f"     - '{song}': {count} times ({percentage:.1f}%)")
    
    # Card diversity analysis
    songs_per_card = [len(set(card_info['songs'])) for card_info in all_cards]
    min_songs = min(songs_per_card)
    max_songs = max(songs_per_card)
    avg_songs = sum(songs_per_card) / len(songs_per_card)
    
    print(f"\n   Songs per card: min={min_songs}, max={max_songs}, avg={avg_songs:.1f}")
    
    # Check for cards with internal duplicates (same song appearing twice in one card)
    cards_with_internal_duplicates = []
    for card_info in all_cards:
        if len(card_info['songs']) != len(set(card_info['songs'])):
            cards_with_internal_duplicates.append(card_info)
    
    if cards_with_internal_duplicates:
        print(f"\n⚠️ Cards with internal duplicates (same song twice): {len(cards_with_internal_duplicates)}")
        for card_info in cards_with_internal_duplicates:
            duplicated_songs = [song for song in set(card_info['songs']) 
                              if card_info['songs'].count(song) > 1]
            print(f"   - {card_info['location']}: {duplicated_songs}")
    else:
        print(f"\n✅ No cards have internal song duplicates")
    
    print(f"={'='*50}")
    
    return len(duplicate_groups) == 0  # Returns True if no duplicates found


# Example usage
if __name__ == "__main__":
    template_path = "template.jpg"

    canciones = [
        "Mi Huelva tiene una Ría",
        "Sevilla tiene un color especial",
        "La Cucaracha",
        "La Mayonesa",
        "El anillo",
        "Gasolina",
        "Paquito el Chocolatero",
        "Que viva España",
        "Eva María",
        "Un rayo de sol",
        "La chica yeyé",
        "Sarandonga",
        "El tractor amarillo",
        "El tiburón",
        "Salir",
        "La barbacoa",
        "Macarena",
        "Aserejé",
        "Waka Waka",
        "Oma yo viazé un corrá",
        "Ese toro enamorao de la luna",
        "La gasolina",
        "Cuando zarpa el amor",
        "Sueño contigo, que más dado",
        "La bicicleta",
        "María",
        "Ave María",
        "Bulería"
    ]

    canciones_ganadoras = [
        "Baby shark",
        "Tengo que impedir esa boda",
        "El padrino",
        "Ay mama!",
        "El taxi",
        "Nos fuimos pa Madrid"
    ]

    num_sheets = 15

    # Generate text variations for bingo cards with unique combinations
    import random
    import itertools
    text_variations = []
    
    # Strategy: Create unique card combinations while maximizing canciones_ganadoras usage
    # Only one card will have ALL canciones_ganadoras (the winner)
    
    # Use more songs from "canciones" to ensure uniqueness, but still prioritize ganadoras
    # We'll use enough songs to create sufficient variety
    songs_needed_from_canciones = min(len(canciones), 20)  # Use up to 20 different canciones
    selected_canciones = canciones[:songs_needed_from_canciones]
    
    # Combined pool for generating variety
    all_available_songs = canciones_ganadoras + selected_canciones
    
    print(f"Strategy: Create unique cards while maximizing canciones_ganadoras usage")
    print(f"- Using ALL {len(canciones_ganadoras)} canciones_ganadoras: {canciones_ganadoras}")
    print(f"- Using {len(selected_canciones)} from canciones: {selected_canciones}")
    print(f"- Total song pool: {len(all_available_songs)} different songs")
    
    # Track used card combinations to avoid duplicates
    used_card_combinations = set()
    
    def generate_unique_card(card_number, is_winner=False):
        """Generate a unique card combination"""
        max_attempts = 1000  # Prevent infinite loops
        attempts = 0
        
        while attempts < max_attempts:
            if is_winner:
                # Winner card has exactly all canciones_ganadoras
                card_songs = canciones_ganadoras.copy()
            else:
                card_songs = []
                
                # For non-winner cards, include 3-5 canciones_ganadoras (never all 6)
                num_ganadoras = 3 + (card_number % 3)  # Varies between 3, 4, and 5
                
                # Select random subset of canciones_ganadoras
                selected_ganadoras = random.sample(canciones_ganadoras, num_ganadoras)
                card_songs.extend(selected_ganadoras)
                
                # Fill remaining slots with songs from selected_canciones
                remaining_slots = 6 - len(card_songs)
                available_canciones = [song for song in selected_canciones]
                
                if remaining_slots > 0:
                    # Add variety by mixing in some canciones
                    fill_songs = random.choices(available_canciones, k=remaining_slots)
                    card_songs.extend(fill_songs)
            
            # Create a signature for this card (sorted to catch duplicates regardless of order)
            card_signature = tuple(sorted(card_songs))
            
            # Check if this combination has been used before
            if card_signature not in used_card_combinations:
                used_card_combinations.add(card_signature)
                return card_songs
            
            attempts += 1
        
        # If we couldn't find a unique combination after many attempts,
        # add more variety by using additional canciones
        print(f"Warning: Adding more songs for uniqueness (card {card_number})")
        if is_winner:
            return canciones_ganadoras.copy()
        else:
            # Force uniqueness by adding a unique song from the extended pool
            extended_pool = canciones[:min(len(canciones), 30)]  # Use more canciones if needed
            card_songs = random.sample(canciones_ganadoras, 3)  # Start with 3 ganadoras
            remaining = random.sample([s for s in extended_pool if s not in card_songs], 3)
            return card_songs + remaining
    
    # Generate pages of bingo cards
    card_number = 0
    for page_num in range(1, num_sheets + 1):
        # Each page contains 8 bingo cards (8 main cells, each with 6 songs)
        page_cards = []
        
        if page_num == 1:
            # First page: ensure one card contains ALL canciones_ganadoras (winning card)
            print(f"Generating Page {page_num} with WINNING CARD...")
            
            # First card on the page is the winning card
            winning_card_songs = generate_unique_card(card_number, is_winner=True)
            page_cards.append(winning_card_songs)
            card_number += 1
            
            # Generate 7 more unique cards for this page
            for card_idx in range(7):
                card_songs = generate_unique_card(card_number)
                page_cards.append(card_songs)
                card_number += 1
            
            print(f"Page {page_num}: Card 1 (WINNING) contains all canciones_ganadoras: {canciones_ganadoras}")
            
        else:
            # Other pages: generate 8 unique cards
            print(f"Generating Page {page_num}...")
            
            for card_idx in range(8):
                card_songs = generate_unique_card(card_number)
                page_cards.append(card_songs)
                card_number += 1
        
        # Add this page to text_variations
        text_variations.append(page_cards)
        
        # Check which canciones_ganadoras are in each card of this page
        for card_idx, card_songs in enumerate(page_cards):
            ganadoras_in_card = [song for song in canciones_ganadoras if song in card_songs]
            if ganadoras_in_card:
                print(f"Page {page_num}, Card {card_idx + 1} contains {len(ganadoras_in_card)} canciones_ganadoras: {ganadoras_in_card}")
    
    # Print summary of song usage
    used_from_canciones = set()
    used_from_ganadoras = set()
    total_ganadora_slots = 0
    total_cancion_slots = 0
    
    for page in text_variations:
        for card in page:
            for song in card:
                if song in canciones_ganadoras:
                    used_from_ganadoras.add(song)
                    total_ganadora_slots += 1
                elif song in canciones:
                    used_from_canciones.add(song)
                    total_cancion_slots += 1
    
    total_slots = total_ganadora_slots + total_cancion_slots
    ganadora_percentage = (total_ganadora_slots / total_slots) * 100
    
    print(f"\n=== OPTIMIZED SONG USAGE SUMMARY ===")
    print(f"Total different songs used: {len(used_from_canciones) + len(used_from_ganadoras)}")
    print(f"Songs from 'canciones': {len(used_from_canciones)} out of {len(canciones)} available ({len(used_from_canciones)}/{len(canciones)} = {len(used_from_canciones)/len(canciones)*100:.1f}%)")
    print(f"Songs from 'canciones_ganadoras': {len(used_from_ganadoras)} out of {len(canciones_ganadoras)} available")
    print(f"")
    print(f"SLOT USAGE OPTIMIZATION:")
    print(f"Total song slots: {total_slots}")
    print(f"Slots filled with canciones_ganadoras: {total_ganadora_slots} ({ganadora_percentage:.1f}%)")
    print(f"Slots filled with canciones: {total_cancion_slots} ({100-ganadora_percentage:.1f}%)")
    print(f"")
    print(f"Songs from 'canciones' used: {sorted(list(used_from_canciones))}")
    print("=====================================")
    
    # Verify uniqueness of all cards
    all_card_signatures = []
    for page_idx, page in enumerate(text_variations):
        for card_idx, card in enumerate(page):
            signature = tuple(sorted(card))
            all_card_signatures.append((signature, page_idx + 1, card_idx + 1))
    
    # Check for duplicates
    signature_counts = {}
    for signature, page, card in all_card_signatures:
        if signature not in signature_counts:
            signature_counts[signature] = []
        signature_counts[signature].append((page, card))
    
    duplicates = {sig: locations for sig, locations in signature_counts.items() if len(locations) > 1}
    
    print(f"\n=== CARD UNIQUENESS VERIFICATION ===")
    print(f"Total cards generated: {len(all_card_signatures)}")
    print(f"Unique card combinations: {len(signature_counts)}")
    
    if duplicates:
        print(f"⚠ WARNING: Found {len(duplicates)} duplicate card combinations:")
        for signature, locations in duplicates.items():
            location_str = ", ".join([f"Page {p} Card {c}" for p, c in locations])
            print(f"  - Duplicate found at: {location_str}")
            print(f"    Songs: {list(signature)}")
    else:
        print("✓ SUCCESS: All cards are unique!")
    
    # Verify only one winner exists
    winner_count = 0
    for page_idx, page in enumerate(text_variations):
        for card_idx, card in enumerate(page):
            if set(card) == set(canciones_ganadoras):
                winner_count += 1
                print(f"WINNER FOUND: Page {page_idx + 1}, Card {card_idx + 1}")
    
    print(f"\nWINNER VERIFICATION: {winner_count} card(s) contain ALL canciones_ganadoras")
    if winner_count == 1:
        print("✓ SUCCESS: Exactly one winning card exists!")
    else:
        print("⚠ WARNING: There should be exactly one winning card!")
    
    print("======================================")
    
    # Create the PDF
    output_pdf = "musical-bingo-cards.pdf"
    create_pdf_with_images(template_path, text_variations, output_pdf)
    
    # Perform comprehensive duplicate checking
    check_for_duplicate_cards(text_variations)
    
    # Try to open the PDF
    try:
        os.startfile(output_pdf)
    except Exception as e:
        print(f"Could not open PDF automatically: {e}")
