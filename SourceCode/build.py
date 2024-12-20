import os
import sys
import subprocess

def build_exe():
    """Build the executable using PyInstaller"""
    # Install required packages if needed
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Simple build command without any icon or extra options
    subprocess.check_call([
        'pyinstaller',
        '--noconfirm',
        '--clean',
        '--windowed',
        '--onefile',
        '--noupx',  # Disable UPX compression
        '--name=ImageGrouper',
        os.path.join('SourceCode', 'image_grouper.py')
    ])

if __name__ == '__main__':
    build_exe() 