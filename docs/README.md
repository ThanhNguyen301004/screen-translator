# Screen Translator

A desktop application for real-time screen translation using OCR and translation APIs.

## Installation

1. Clone the repository: `git clone <repo-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Install Tesseract OCR: Download from https://github.com/tesseract-ocr/tesseract and set path in ocr_engine.py
4. Run: `python src/main.py`

## Usage

- Press Ctrl+Shift+T to select a screen area.
- The translated text will overlay on the screen.

## Configuration

Edit `config/config.json` for default languages and API keys.

## Testing

Run tests: `python -m unittest discover tests`