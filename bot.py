import os
import sys
import asyncio
import tempfile
import logging
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv
from markitdown import MarkItDown
import pytesseract
from PIL import Image, ImageOps

# Load env
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_BOT_TOKEN not found in .env")
    sys.exit(1)

# Tesseract config
TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("bot-md-converter")

# MarkItDown instance
md = MarkItDown()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    log.info(f"Bot online: {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help | MD Converter"))


@bot.command(name="convert", aliases=["md", "tomd"])
async def convert_file(ctx):
    """Convert attached file to Markdown. Usage: !convert [attach file]"""
    if not ctx.message.attachments:
        await ctx.send("Attach a file! Usage: `!convert` + attach file")
        return

    attachment = ctx.message.attachments[0]
    filename = attachment.filename
    file_size = attachment.size

    # Check size limit (50MB)
    if file_size > 50 * 1024 * 1024:
        await ctx.send(f"File `{filename}` too large ({file_size // 1024 // 1024}MB). Max 50MB.")
        return

    await ctx.send(f"Converting `{filename}`...")

    # Download to temp
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / filename
        try:
            await attachment.save(tmp_path)
        except Exception as e:
            await ctx.send(f"Download failed: {e}")
            return

        # Convert (non-blocking)
        try:
            markdown_text = await asyncio.to_thread(md.convert, str(tmp_path))
            markdown_text = markdown_text.text_content
        except Exception as e:
            await ctx.send(f"Conversion failed: {e}")
            log.error(f"Conversion error for {filename}: {e}")
            return

    if not markdown_text or not markdown_text.strip():
        await ctx.send(f"`{filename}` produced empty output. Format may not be supported.")
        return

    # Send as .md file attachment
    md_filename = Path(filename).stem + ".md"
    md_path = Path(tempfile.gettempdir()) / f"mdbot_{md_filename}"
    md_path.write_text(markdown_text, encoding="utf-8")

    try:
        await ctx.send(file=discord.File(str(md_path), filename=md_filename))
    finally:
        md_path.unlink(missing_ok=True)

    log.info(f"Converted: {filename} -> {md_filename} ({len(markdown_text)} chars)")


@bot.command(name="url")
async def convert_url(ctx, url: str = None):
    """Convert URL to Markdown. Usage: !url https://example.com"""
    if not url:
        await ctx.send("Provide a URL! Usage: `!url https://example.com`")
        return

    await ctx.send(f"Converting `{url}`...")

    try:
        result = md.convert(url)
        markdown_text = result.text_content
    except Exception as e:
        await ctx.send(f"Conversion failed: {e}")
        return

    if not markdown_text or not markdown_text.strip():
        await ctx.send("URL produced empty output.")
        return

    md_filename = "webpage.md"
    md_path = Path(tempfile.gettempdir()) / f"mdbot_{md_filename}"
    md_path.write_text(markdown_text, encoding="utf-8")

    try:
        await ctx.send(file=discord.File(str(md_path), filename=md_filename))
    finally:
        md_path.unlink(missing_ok=True)

    log.info(f"Converted URL: {url} ({len(markdown_text)} chars)")


def _preprocess_for_ocr(image_path: str) -> Image.Image:
    """Grayscale + threshold for better OCR accuracy."""
    img = Image.open(image_path)
    img = ImageOps.grayscale(img)
    img = img.point(lambda x: 0 if x < 128 else 255, "1")
    return img


@bot.command(name="ocr")
async def ocr_image(ctx, *, args: str = ""):
    """OCR via Tesseract. Usage: !ocr [lang=eng+ind] [attach image]"""
    # Parse optional lang= argument
    lang = "eng+ind"
    if args:
        parts = args.strip().split()
        for p in parts:
            if p.startswith("lang="):
                lang = p.split("=", 1)[1]

    if not ctx.message.attachments:
        await ctx.send("Attach an image! Usage: `!ocr` + attach image")
        return

    attachment = ctx.message.attachments[0]
    filename = attachment.filename.lower()

    if not filename.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")):
        await ctx.send("Only image files supported for OCR.")
        return

    # Size check
    if attachment.size > 50 * 1024 * 1024:
        await ctx.send(f"File too large ({attachment.size // 1024 // 1024}MB). Max 50MB.")
        return

    # Tesseract installed check
    if not Path(TESSERACT_PATH).exists():
        await ctx.send(
            "Tesseract not installed. Download: "
            "https://github.com/UB-Mannheim/tesseract/wiki"
        )
        return

    await ctx.send(f"Running OCR on `{attachment.filename}` (lang=`{lang}`)...")

    text = ""
    img_w, img_h = "?", "?"
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / attachment.filename
            await attachment.save(tmp_path)

            # Read dimensions before temp cleanup
            with Image.open(tmp_path) as img:
                img_w, img_h = img.size

            # Preprocess + OCR (non-blocking with timeout)
            def run_ocr():
                preprocessed = _preprocess_for_ocr(str(tmp_path))
                return pytesseract.image_to_string(preprocessed, lang=lang)

            try:
                text = await asyncio.wait_for(
                    asyncio.to_thread(run_ocr), timeout=30
                )
            except asyncio.TimeoutError:
                await ctx.send("OCR timed out after 30s — image may be too large or complex.")
                return

    except Exception as e:
        await ctx.send(f"OCR error: {e}")
        log.error(f"OCR error for {attachment.filename}: {e}")
        return

    if not text or not text.strip():
        await ctx.send("OCR returned no text — image may be blank, unreadable, or unsupported.")
        return

    # Build Markdown output

    md_content = (
        f"# OCR: {attachment.filename}\n"
        f"**Language:** {lang}\n"
        f"**Size:** {img_w}x{img_h}px\n"
        f"---\n"
        f"{text.strip()}\n"
    )

    md_filename = Path(attachment.filename).stem + "_ocr.md"
    md_path = Path(tempfile.gettempdir()) / f"mdbot_{md_filename}"
    try:
        md_path.write_text(md_content, encoding="utf-8")
        await ctx.send(file=discord.File(str(md_path), filename=md_filename))
    finally:
        md_path.unlink(missing_ok=True)

    log.info(f"OCR: {attachment.filename} lang={lang} ({len(text)} chars)")


@bot.command(name="help")
async def help_cmd(ctx):
    """Show available commands."""
    embed = discord.Embed(
        title="MD Converter Bot",
        description="Convert any file or URL to Markdown using MarkItDown",
        color=0x5865F2
    )
    embed.add_field(
        name="!convert",
        value="Convert attached file to .md\nUsage: `!convert` + attach file",
        inline=False
    )
    embed.add_field(
        name="!url <link>",
        value="Convert webpage to .md\nUsage: `!url https://example.com`",
        inline=False
    )
    embed.add_field(
        name="!ocr",
        value="Extract text from image via Tesseract OCR\n"
              "Usage: `!ocr` + attach image\n"
              "Language: `!ocr lang=ind` or `!ocr lang=eng+ind`",
        inline=False
    )
    embed.add_field(
        name="Supported formats",
        value="PDF, Word, Excel, PowerPoint, HTML, Images, Audio, "
              "CSV, JSON, XML, ZIP, YouTube URLs, EPub",
        inline=False
    )
    await ctx.send(embed=embed)


# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param.name}")
        return
    log.error(f"Command error: {error}")
    await ctx.send(f"Error: {error}")


# Run
log.info("Starting MD Converter Bot...")
bot.run(TOKEN)
