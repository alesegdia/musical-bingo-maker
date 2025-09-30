# Musical Bingo Maker

A Python application that creates customizable musical bingo cards with text overlays and generates PDF output for printing.

## Features

- Load custom template images
- Add text to grid cells with custom fonts
- Generate PDF files with multiple bingo cards
- Configurable grid layout (2x4 cells by default)
- Support for custom fonts (TrueType)

## Requirements

- Python 3.7 or higher
- Pillow (PIL) for image processing
- ReportLab for PDF generation

## Quick Setup

### Option 1: Automated Setup (Recommended)

**For Windows users:**
```bash
# Double-click setup.bat or run in Command Prompt/PowerShell:
setup.bat
```

**For Linux/Mac users:**
```bash
# Make the script executable and run:
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Clone the repository:**
```bash
git clone https://github.com/alesegdia/musical-bingo-maker.git
cd musical-bingo-maker
```

2. **Create a virtual environment:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

**After setup, you can run the musical bingo maker:**

```bash
# If virtual environment is activated:
python musical-bingo-maker.py

# Or run directly without activating:
# Windows:
.venv\Scripts\python.exe musical-bingo-maker.py

# Linux/Mac:
.venv/bin/python musical-bingo-maker.py
```

### Files in the Project

- `musical-bingo-maker.py` - Main application script
- `template.jpg` - Template image for the bingo cards
- `JandaManateeSolid.ttf` - Custom font file
- `requirements.txt` - Python dependencies
- `setup.bat` / `setup.sh` - Automated setup scripts

## Customization

- Replace `template.jpg` with your own template image
- Modify the cell text content in the Python script
- Change the font by replacing `JandaManateeSolid.ttf` or updating the font path
- Adjust grid dimensions by modifying the `cols` and `rows` variables

## Output

The application generates:
- Individual bingo card images
- A compiled PDF file (`musical_bingo_cards.pdf`) ready for printing

## Dependencies

- **Pillow (11.3.0)** - Image processing and manipulation
- **ReportLab (4.4.4)** - PDF generation

## Troubleshooting

- Ensure Python 3.7+ is installed and available in your PATH
- If font loading fails, the application will fall back to the default font
- Check that all required files (template.jpg, font file) are present in the project directory
