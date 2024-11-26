from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

@app.get("/generate_label/")
async def generate_label(
    code: str,
    url: str,
    width_mm: float = Query(45.7, description="Width of the label in millimeters"),
    height_mm: float = Query(21.2, description="Height of the label in millimeters"),
    font_size: int = Query(24, description="Font size for the text")
):
    # Crear el código QR
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir dimensiones de la etiqueta a píxeles
    dpi = 300
    width_px = int(width_mm * 3.7795275591)
    height_px = int(height_mm * 3.7795275591)
    print(width_px)
    print(height_px)
    
    label = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(label)

    # Pegar el código QR en la etiqueta
    qr_size = min(width_px // 2, height_px)
    qr_img = qr_img.resize((qr_size, qr_size))
    label.paste(qr_img, (10, (height_px - qr_size) // 2))

    # Establecer una fuente TrueType con un tamaño predeterminado
    try:
        font_path = "fonts/Roboto-Black.ttf"  # Cambia la ruta según tu sistema
        font = ImageFont.truetype(font_path, size=font_size)
    except IOError:
        raise RuntimeError("No se pudo cargar la fuente. Asegúrate de que exista una fuente TTF válida en la ruta especificada.")

    # Calcular las dimensiones del texto usando textbbox
    text_bbox = draw.textbbox((0, 0), code, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Posicionar el texto
    text_x = qr_size + 20
    text_y = (height_px - text_height) // 2
    draw.text((text_x, text_y), code, fill="black", font=font)

    # Guardar la etiqueta en un buffer para retornar
    buffer = BytesIO()
    label.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")