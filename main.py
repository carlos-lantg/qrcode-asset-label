from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()


@app.get("/generate_label/")
async def generate_label(
    code: str, url: str, width_mm: float, height_mm: float, font_size: int
):
    # Create the QR Code
    qr = qrcode.QRCode(
        box_size=4, border=2, error_correction=qrcode.constants.ERROR_CORRECT_L
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convert dimensions to pixels
    dpi = 300
    width_px = int(width_mm * 3.7795275591)
    height_px = int(height_mm * 3.7795275591)

    label = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(label)

    # Add the QR code to the label
    qr_size = min(width_px // 2, height_px)
    qr_img = qr_img.resize((qr_size, qr_size))
    label.paste(qr_img, (10, (height_px - qr_size) // 2))

    # Load the font
    try:
        font_path = "fonts/Roboto-Black.ttf"
        font = ImageFont.truetype(font_path, size=font_size)
    except IOError:
        raise RuntimeError(
            "Could not load the font. Ensure a valid TTF font file is available at the specified path."
        )

    # Calculate maximum text width
    text_x = qr_size + 20
    max_text_width = width_px - text_x - 10
    max_text_height = height_px

    # Adjust font size dynamically
    while True:
        words = code.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        line_height = draw.textbbox((0, 0), "hg", font=font)[3]
        total_text_height = line_height * len(lines)

        if total_text_height <= max_text_height and all(
            draw.textbbox((0, 0), line, font=font)[2]
            - draw.textbbox((0, 0), line, font=font)[0]
            <= max_text_width
            for line in lines
        ):
            break  # Font size is small enough to fit
        font_size -= 2  # Reduce font size
        font = ImageFont.truetype(font_path, size=font_size)

    # Center the text vertically
    start_y = (height_px - total_text_height) // 2

    # Draw the text
    for i, line in enumerate(lines):
        line_y = start_y + i * line_height
        draw.text((text_x, line_y), line, fill="black", font=font)

    # Save the label to a buffer
    buffer = BytesIO()
    label.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
