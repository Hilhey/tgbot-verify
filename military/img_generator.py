"""Military ID card PNG generator."""
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a basic font with a fallback to default."""
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def generate_military_id_card(
    first_name: str,
    last_name: str,
    branch_name: str,
    service_id: str,
    rank: str,
    birth_date: str,
    death_date: str,
) -> bytes:
    """Generate a simple military ID card PNG."""
    width, height = 900, 560
    card = Image.new("RGB", (width, height), color=(20, 34, 46))
    draw = ImageDraw.Draw(card)

    header_height = 90
    draw.rectangle([0, 0, width, header_height], fill=(10, 20, 32))
    draw.rectangle([0, header_height, width, header_height + 8], fill=(186, 156, 70))

    title_font = _load_font(32)
    label_font = _load_font(18)
    value_font = _load_font(24)

    draw.text((30, 24), "MILITARY IDENTIFICATION", font=title_font, fill=(255, 255, 255))
    draw.text((30, 120), "Branch", font=label_font, fill=(200, 200, 200))
    draw.text((30, 150), branch_name, font=value_font, fill=(255, 255, 255))

    draw.text((30, 210), "Name", font=label_font, fill=(200, 200, 200))
    draw.text(
        (30, 240),
        f"{first_name} {last_name}",
        font=value_font,
        fill=(255, 255, 255),
    )

    draw.text((30, 300), "Rank", font=label_font, fill=(200, 200, 200))
    draw.text((30, 330), rank, font=value_font, fill=(255, 255, 255))

    draw.text((30, 390), "Service ID", font=label_font, fill=(200, 200, 200))
    draw.text((30, 420), service_id, font=value_font, fill=(255, 255, 255))

    draw.text((520, 120), "Birth Date", font=label_font, fill=(200, 200, 200))
    draw.text((520, 150), birth_date, font=value_font, fill=(255, 255, 255))
    draw.text((520, 210), "Death Date", font=label_font, fill=(200, 200, 200))
    draw.text((520, 240), death_date, font=value_font, fill=(255, 255, 255))

    issued = datetime.now().strftime("%Y-%m-%d")
    expires = datetime.now().replace(year=datetime.now().year + 3).strftime("%Y-%m-%d")
    draw.text((520, 300), "Issued", font=label_font, fill=(200, 200, 200))
    draw.text((520, 330), issued, font=value_font, fill=(255, 255, 255))
    draw.text((520, 390), "Expires", font=label_font, fill=(200, 200, 200))
    draw.text((520, 420), expires, font=value_font, fill=(255, 255, 255))

    # Placeholder photo block (deterministic pattern)
    photo_x, photo_y = 620, 120
    draw.rectangle([photo_x, photo_y, photo_x + 220, photo_y + 220], outline=(186, 156, 70), width=3)
    offsets = [(20, 30), (80, 60), (140, 40), (60, 120), (120, 160), (180, 110)]
    for x_offset, y_offset in offsets:
        x = photo_x + x_offset
        y = photo_y + y_offset
        draw.ellipse([x, y, x + 6, y + 6], fill=(186, 156, 70))

    buffer = BytesIO()
    card.save(buffer, format="PNG")
    return buffer.getvalue()
