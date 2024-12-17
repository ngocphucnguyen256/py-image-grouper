import os
import sys
import subprocess
from PIL import Image

def create_icon():
    """Create a simple icon for the application"""
    icon_size = (256, 256)
    icon = Image.new('RGBA', icon_size, (76, 175, 80))  # Green color
    
    # Save as ICO in the SourceCode directory
    icon_path = os.path.join('SourceCode', 'app_icon.ico')
    icon.save(icon_path, format='ICO', sizes=[(256, 256)])
    return icon_path

def build_exe():
    """Build the executable using PyInstaller"""
    # Create icon if it doesn't exist
    icon_path = os.path.join('SourceCode', 'app_icon.ico')
    if not os.path.exists(icon_path):
        create_icon()
    
    # Install required packages
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Change to SourceCode directory
    os.chdir('SourceCode')
    
    # Build the executable using spec file
    subprocess.check_call([
        'pyinstaller',
        '--clean',
        'image_grouper.spec'
    ])
    
    # Move back to original directory
    os.chdir('..')

if __name__ == '__main__':
    build_exe() 