# Markdown Remover by Clark & Burke, LLC

- **Version**: v1.0.0
- **Date**: 10.26.2024
- **Written by**: Geoff Clark of Clark & Burke, LLC

- **README.md Last Updated**: 10.26.2024

Markdown Remover is a GUI-based tool written in Python using PyQt6 that strips markdown syntax
from markdown files, converting them into plain text. Originally created to clean up ChatGPT-
generated technical support responses for customer communication, this tool has evolved to be
useful for any scenario where you need to extract clean, readable text from markdown documents
without formatting characters.

## Getting Started

These instructions will help you set up and run the Markdown Remover on your local machine.

## Prerequisites

- Python 3.11.8 or higher (strictly required)
- PyQt6 (automatically installed during setup)
- For Linux: X11 or Wayland desktop environment
- For macOS: OS X 10.10 or higher

## Installation

The application includes automated installers for both Windows and Unix-based systems:

### Windows Installation

Run the PowerShell installer as administrator:

```powershell
.\installer.ps1
```

The installer will:

1. Verify Python 3.11.8+ is installed
2. Create a virtual environment (.venv-HOSTNAME)
3. Install required dependencies
4. Create a desktop shortcut
5. Generate launch_app.ps1

### Linux/macOS Installation

Run the bash installer:

```bash
chmod +x installer.sh
./installer.sh
```

The installer will:

1. Verify Python 3.11.8+ is installed
2. Create a virtual environment (.venv-HOSTNAME)
3. Install required dependencies
4. For Linux: Create an application shortcut in the system menu
5. For macOS: Create a proper .app bundle in the current directory
6. Generate launch_app.sh

## Running the Application

### Windows

- Double-click the "Launch Markdown Stripper" shortcut on your desktop, or
- Run `.\launch_app.ps1` from PowerShell

### Linux

- Launch from your application menu, or
- Run `./launch_app.sh` from terminal

### macOS

- Double-click the "Markdown Stripper.app" bundle, or
- Run `./launch_app.sh` from terminal

### Using the Application

1. The application provides a GUI interface with:

   - A "Copy Prompt" button to copy template text (from prompt.txt)
   - Input text area for pasting markdown text
   - Process button to strip markdown formatting
   - Output text area showing cleaned text
   - Copy, Clear, and Exit buttons
   - Settings menu for configuration

2. Features:
   - Strips common markdown syntax (headers, bold, italic, links, code blocks)
   - Automatically copies processed text to clipboard
   - Preserves content while removing formatting
   - Saves window position and size per machine
   - Dark mode support
   - Settings dialog for configuration

## Application Files

- `markdown_stripper.py`: Main application code
- `installer.ps1`: Windows PowerShell installer
- `installer.sh`: Unix bash installer
- `requirements.txt`: Python package dependencies
- `prompt.txt`: Template text for support responses

## Settings

The application stores settings in a SQLite database named after your hostname
(HOSTNAME.settings), including:

- Window position and size
- Prompt file location
- Other user preferences

## Future Features

- Support for processing directories of markdown files
- Output formatting options (e.g., retaining headings, lists)
- Interactive mode with progress indicators
- Additional theme options
- Batch processing capabilities

## Update Notes

### Version 1.0.0 - 10.26.2024

- Initial release with GUI interface
- Markdown stripping functionality
- Settings persistence
- Cross-platform support
- Automated installers

## Author Information

- **Author**: [Geoff Clark of Clark & Burke, LLC](https://www.cnb.llc)
- **Email**: [geoff@cnb.llc](mailto:geoff@cnb.llc)
- **Socials**:
  [GitHub @aznironman](https://github.com/aznironman)
  [IG: @cnbllc](https://instagram.com/cnbllc)
  [X: @clarkandburke](https://www.x.com/clarkandburke)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Attribution

If you use this software as a base for your own projects or fork it, we kindly request that
you give credit to Clark & Burke, LLC. While not required by the license, it is appreciated
and helps support the ongoing development of this project.

## Third-Party Notices

All rights reserved by their respective owners. Users must comply with the licenses and terms
of service of the software being installed.
