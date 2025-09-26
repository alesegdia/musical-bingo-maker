from PIL import Image, ImageDraw, ImageFont
import os

# Load the image
template_path = "template.jpg"
output_path = "template_with_text.jpg"
image = Image.open(template_path)

draw = ImageDraw.Draw(image)


# Define grid parameters
cols = 2
rows = 4
cell_texts = [f"Cell {i+1}" for i in range(cols * rows)]  # Replace with your own text list if needed

# Get image size
img_width, img_height = image.size
cell_width = img_width // cols
cell_height = img_height // rows


# Load a TrueType font with a larger size
font_path = "arial.ttf"  # You can use any TTF font available on your system
font_size = 48  # Increase this value for even bigger text
font = ImageFont.truetype(font_path, font_size)

# Write text in the center of each cell


for idx, text in enumerate(cell_texts):
	col = idx % cols
	row = idx // cols
	x0 = col * cell_width
	y0 = row * cell_height


	# Draw the cell bounding box with much thicker lines (green)
	draw.rectangle([x0, y0, x0 + cell_width, y0 + cell_height], outline=(0, 255, 0), width=10)


	# Editable parameters for blue inner rectangle (in pixels)
	blue_x_offset = 45   # pixels from left edge of cell
	blue_y_offset = 140   # pixels from top edge of cell
	blue_width = 650      # width in pixels
	blue_height = 330     # height in pixels

	inner_x0 = x0 + blue_x_offset
	inner_y0 = y0 + blue_y_offset
	inner_x1 = inner_x0 + blue_width
	inner_y1 = inner_y0 + blue_height
	draw.rectangle([inner_x0, inner_y0, inner_x1, inner_y1], outline=(0, 0, 255), width=6)

	# Calculate inner cell sizes
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

	# Add text to each red table cell (2 rows x 3 columns = 6 cells per main cell)
	inner_cell_texts = [f"R{r+1}C{c+1}" for r in range(inner_rows) for c in range(inner_cols)]
	
	for inner_idx, inner_text in enumerate(inner_cell_texts):
		inner_col = inner_idx % inner_cols
		inner_row = inner_idx // inner_cols
		
		# Calculate position of this inner cell
		inner_cell_x0 = inner_x0 + inner_col * inner_cell_width
		inner_cell_y0 = inner_y0 + inner_row * inner_cell_height
		inner_cell_x1 = inner_cell_x0 + inner_cell_width
		inner_cell_y1 = inner_cell_y0 + inner_cell_height
		
		# Dynamically find the largest font size that fits in the inner cell
		max_font_size = 10
		max_possible_size = min(inner_cell_width, inner_cell_height) // 2
		for size in range(10, max_possible_size, 2):
			test_font = ImageFont.truetype(font_path, size)
			bbox = test_font.getbbox(inner_text)
			text_width = bbox[2] - bbox[0]
			text_height = bbox[3] - bbox[1]
			# Add some padding by checking against 80% of cell size
			if text_width < inner_cell_width * 0.8 and text_height < inner_cell_height * 0.8:
				max_font_size = size
			else:
				break
		
		# Use the largest fitting font size
		final_font = ImageFont.truetype(font_path, max_font_size)
		bbox = final_font.getbbox(inner_text)
		text_width = bbox[2] - bbox[0]
		text_height = bbox[3] - bbox[1]
		
		# Center the text in the inner cell
		text_x = inner_cell_x0 + (inner_cell_width - text_width) // 2
		text_y = inner_cell_y0 + (inner_cell_height - text_height) // 2
		
		draw.text((text_x, text_y), inner_text, font=final_font, fill=(255, 255, 255))



# (Grid text drawing is now handled above)


# Save the new image
image.save(output_path)
print(f"Text added and saved to {output_path}")

# Show the processed image for quick viewing (Windows)
try:
    os.startfile(output_path)
except Exception as e:
    print(f"Could not open image automatically: {e}")
