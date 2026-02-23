# Screen Translator

A desktop application for real-time screen text translation using OCR (Optical Character Recognition) and machine translation APIs. Capture any area of your screen, extract text, and get instant translations displayed as an overlay.

## Features

- **Real-time Screen Capture**: Select any rectangular area on your screen using a hotkey.
- **OCR Text Extraction**: Uses Tesseract OCR engine with advanced image preprocessing for accurate text recognition from various backgrounds and fonts.
- **Machine Translation**: Integrates with Google Translate API for fast, high-quality translations.
- **Interactive Overlay**: Displays original and translated text in a draggable, resizable window with options to:
  - Change source and target languages
  - Recapture the same area
  - Copy text to clipboard
  - Text-to-speech (TTS) playback
- **System Tray Integration**: Runs in the background with a tray icon for easy access.
- **Multi-language Support**: Supports 50+ languages for both OCR and translation.
- **Configurable Settings**: Customize default languages, API keys, and OCR settings via JSON configuration files.
- **Cross-platform**: Built with Python and works on Windows (with potential for other platforms).

## Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11 (primary support)
- **Tesseract OCR**: Version 5.0 or higher (download from [GitHub](https://github.com/tesseract-ocr/tesseract))
- **Dependencies**: See `requirements.txt` for full list

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd screen-translator
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**:
   - Download and install Tesseract from [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
   - Add Tesseract to your system PATH, or update the path in `src/ocr/ocr_engine.py`:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```
   - Download language data packs for supported languages (e.g., `eng`, `vie`, `chi_sim`, etc.)

4. **(Optional) Install additional TTS dependencies**:
   ```bash
   pip install gtts pygame pyperclip
   ```

## Usage

1. **Run the application**:
   ```bash
   python src/main.py
   ```
   The app will start in the system tray.

2. **Capture and translate**:
   - Press `Ctrl+Shift+L` to enter screen selection mode
   - Click and drag to select a rectangular area containing text
   - Release to capture, OCR, translate, and display the overlay

3. **Interact with overlay**:
   - Drag the overlay window to reposition
   - Use dropdowns to change source/target languages
   - Click "Recapture" to scan the same area again
   - Click "Copy" to copy translated text to clipboard
   - Click speaker icon for text-to-speech

4. **Settings**:
   - Edit `config/config.json` to change default languages and settings
   - Supported languages are listed in `config/languages.json`

## Configuration

The application uses JSON configuration files in the `config/` directory:

- **`config.json`**: Main settings
  ```json
  {
    "source_lang": "en",
    "target_lang": "vi",
    "api_key": "",
    "ocr_lang": "eng"
  }
  ```

- **`languages.json`**: List of supported languages for UI dropdowns

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller ScreenTranslator.spec
```

The executable will be created in the `dist/` directory.

## Testing

Run the test suite:

```bash
python -m unittest discover tests
```

Individual test files:
- `test_capture.py`: Screen capture functionality
- `test_ocr.py`: OCR text extraction
- `test_overlay.py`: Overlay display
- `test_translation.py`: Translation services

## Architecture

The application follows a modular architecture:

- **`ui/`**: User interface components (main app, tray icon, settings)
- **`capture/`**: Screen capture using `mss` library with DPI scaling support
- **`ocr/`**: Text extraction using Tesseract with image preprocessing
- **`translation/`**: Translation using Google Translate API
- **`overlay/`**: Interactive display window with TTS and clipboard integration
- **`utils/`**: Logging, error handling, and helper functions

See `docs/architecture.md` for detailed component descriptions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Specify your license here, e.g., MIT License]

## Troubleshooting

- **OCR not working**: Ensure Tesseract is installed and PATH is set correctly
- **Translation errors**: Check internet connection and API limits
- **Hotkey not responding**: Make sure no other applications are using the same hotkey
- **DPI scaling issues**: The app handles Windows DPI scaling automatically

## Dependencies

Key libraries used:
- `tkinter`: GUI framework
- `mss`: Screen capture
- `pytesseract`: OCR engine interface
- `opencv-python`: Image processing
- `googletrans`: Translation API
- `keyboard`: Global hotkeys
- `pillow`: Image handling
- `pyinstaller`: Executable building