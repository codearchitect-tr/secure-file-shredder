"""
Secure File Shredder - Main Launcher
Military-grade file destruction tool
"""

from gui import ModernShredderGUI


def main():
    """Launch the application"""
    app = ModernShredderGUI()
    app.run()


if __name__ == "__main__":
    main()
