# Bot MD Converter

Discord bot to convert any file to Markdown format using [MarkItDown](https://github.com/microsoft/markitdown).

## Features

- Convert file attachments to `.md` (PDF, Word, Excel, PowerPoint, HTML, Images, Audio, CSV, JSON, XML, ZIP, EPub)
- Convert webpages/URLs to Markdown
- OCR text extraction from images
- Clean output - sends `.md` file directly without chat spam

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!convert` | Convert attached file to .md | `!convert` + attach file |
| `!url <link>` | Convert webpage to .md | `!url https://example.com` |
| `!ocr` | Extract text via Tesseract OCR | `!ocr` + attach image |
| `!ocr lang=ind` | OCR with specific language | `!ocr lang=ind` + attach image |
| `!help` | Show command list | `!help` |

## Setup

### 1. Python Dependencies

```bash
pip install discord.py python-dotenv markitdown pytesseract Pillow
```

Or use `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR (required for `!ocr` command)

1. Download the UB-Mannheim installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default path: `C:\Program Files\Tesseract-OCR\`
3. During installation, ensure language packs for **English** and **Indonesian** are selected
4. Verify installation:
   ```bash
   "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
   ```

If you install Tesseract to a custom path, set `TESSERACT_PATH` in `.env`:

```env
TESSERACT_PATH=C:\custom\path\to\tesseract.exe
```

### 3. Discord Bot Token

1. Create bot at [Discord Developer Portal](https://discord.com/developers/applications)
2. Go to **Bot** tab → Reset Token → copy token
3. Enable **Message Content Intent**
4. Invite bot to server (scope: `bot`, permissions: Send Messages, Attach Files, Read Message History)

### 4. Environment Variables

Create `.env` file:

```env
DISCORD_BOT_TOKEN=your_token_here
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 5. Run Bot

```bash
python bot.py
```

## Supported Formats

- **Documents**: PDF, DOCX, PPTX, XLSX
- **Web**: HTML, URLs, YouTube links
- **Images**: PNG, JPG, JPEG, WEBP, GIF, BMP (with OCR)
- **Data**: CSV, JSON, XML
- **Audio**: MP3, WAV (transcription via Whisper if available)
- **Archives**: ZIP
- **Ebooks**: EPUB

## Example Usage

**Convert PDF:**
```
User: !convert [attach report.pdf]
Bot: [sends report.md]
```

**Convert webpage:**
```
User: !url https://news.ycombinator.com
Bot: [sends webpage.md]
```

**OCR image (default eng+ind):**
```
User: !ocr [attach screenshot.png]
Bot: [sends screenshot_ocr.md]
```

**OCR dengan bahasa spesifik:**
```
User: !ocr lang=ind [attach nota.jpg]
Bot: [sends nota_ocr.md]
```

## Notes

- Max file size: 50MB
- `!ocr` uses Tesseract OCR (default language: `eng+ind`)
- MarkItDown conversion runs asynchronously (non-blocking)
- Output is sent as file attachment only, no preview in chat (clean output)

## Credits

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [discord.py](https://github.com/Rapptz/discord.py)

## License

MIT
