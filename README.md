# Image Grouper

A simple application to sort images into folders based on their aspect ratio (horizontal or vertical).

## Features
- Sort images automatically based on aspect ratio
- User-friendly GUI interface
- Undo functionality to revert the last sorting operation
- Test image generation for trying out the app

## Setup

1. Install Python 3.8 or higher
2. Install requirements:
```bash
pip install -r SourceCode/requirements.txt
```

## Usage

1. Run the application:
```bash
python SourceCode/image_grouper.py
```

2. Use the GUI to:
   - Select Pool folder (source images)
   - Select Horizontal folder (destination for wide images)
   - Select Vertical folder (destination for tall images)
   - Click "Group Images" to start sorting
   - Use "Undo Last Operation" to revert changes
   - Generate test images with "Generate Test Images"

## Creating Executable

To create an executable:

1. Install auto-py-to-exe:
```bash
pip install auto-py-to-exe
```

2. Run:
```bash
auto-py-to-exe
```

3. In the GUI:
   - Select `SourceCode/image_grouper.py` as Script Location
   - Choose "One File" and "Window Based"
   - Click "Convert .py to .exe" 