# Bot MD Converter

Discord bot untuk convert file apapun ke format Markdown menggunakan [MarkItDown](https://github.com/microsoft/markitdown).

## Features

- Convert file attachment ke `.md` (PDF, Word, Excel, PowerPoint, HTML, Images, Audio, CSV, JSON, XML, ZIP, EPub)
- Convert webpage/URL ke Markdown
- OCR text dari gambar
- Output langsung kirim file `.md`, tanpa spam di chat

## Commands

| Command | Deskripsi | Usage |
|---------|-----------|-------|
| `!convert` | Convert attached file ke .md | `!convert` + attach file |
| `!url <link>` | Convert webpage ke .md | `!url https://example.com` |
| `!ocr` | OCR text dari attached image | `!ocr` + attach image |
| `!help` | Show command list | `!help` |

## Setup

### 1. Requirements

```bash
pip install discord.py python-dotenv markitdown
```

### 2. Discord Bot Token

1. Buat bot di [Discord Developer Portal](https://discord.com/developers/applications)
2. Tab **Bot** → Reset Token → copy token
3. Enable **Message Content Intent**
4. Invite bot ke server (scope: `bot`, permissions: Send Messages, Attach Files, Read Message History)

### 3. Environment Variables

Buat file `.env`:

```env
DISCORD_BOT_TOKEN=paste_token_di_sini
```

### 4. Run Bot

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

**OCR image:**
```
User: !ocr [attach screenshot.png]
Bot: [sends screenshot_ocr.md]
```

## Notes

- Max file size: 50MB
- MarkItDown conversion berjalan async (ga block bot)
- Output cuma file attachment, ga ada preview di chat (biar ga berisik)

## Credits

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [discord.py](https://github.com/Rapptz/discord.py)

## License

MIT
