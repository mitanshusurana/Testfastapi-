from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import uuid
import boto3
from rembg import remove
import io

app = FastAPI()

def remove_background(image: Image.Image):
    return remove(image)
 
def enhance_shine(image: Image.Image, factor=1.3):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)
 
def add_professional_background(image: Image.Image, color=(245, 245, 245), blur_radius=3):
    image = image.convert("RGBA")
    np_image = np.array(image)
    alpha = np_image[:, :, 3]
    blurred_alpha = cv2.GaussianBlur(alpha, (0, 0), blur_radius)
    np_image[:, :, 3] = blurred_alpha
    blurred_image = Image.fromarray(np_image)
    background = Image.new("RGBA", image.size, color + (255,))
    composite = Image.alpha_composite(background, blurred_image)
    return composite.convert("RGB")
 
def add_soft_light(image: Image.Image, brightness_factor=1.1, color_boost=1.05):
    enhancer_bright = ImageEnhance.Brightness(image)
    image = enhancer_bright.enhance(brightness_factor)
    enhancer_color = ImageEnhance.Color(image)
    return enhancer_color.enhance(color_boost)
 
def process_gemstone_image(file: UploadFile) -> Image.Image:
    original = Image.open(io.BytesIO(file.file.read())).convert("RGBA")
    no_bg = remove_background(original)
    shiny = enhance_shine(no_bg)
    soft_bg = add_professional_background(shiny)
    final = add_soft_light(soft_bg)
    return final
 
# === UPLOAD TO R2 ===
def upload_to_r2(image: Image.Image, filename: str) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
 
    # === Cloudflare R2 config from Angular environment ===
    s3 = boto3.client(
        "s3",
        endpoint_url="https://3145274f44bbf3178e1f2469ff4fdb07.r2.cloudflarestorage.com",
        aws_access_key_id="ca9f0b53ef7d56c44f56a4edd5d25178",
        aws_secret_access_key="542177ed8b4b9fe82e7b1258dc762043b46f92fbf68ecdd2bfb8f1a3832b7ed3",
        region_name="auto"  # Cloudflare uses 'auto' region
    )
    bucket_name = "suranagemsassets"
    r2_key = f"processed/{filename}.jpg"  # Use f-string for variable substitution
 
    s3.upload_fileobj(buffer, bucket_name, r2_key, ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"})
 
    return f"https://pub-edd8f524b4784df1b5961ce0d431f767.r2.dev/{r2_key}"  # Use f-string for the URL
 
# === FASTAPI ROUTE ===
 
@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    try:
        processed_image = process_gemstone_image(file)
        file_id = str(uuid.uuid4())
        url = upload_to_r2(processed_image, file_id)
        return JSONResponse(content={"imageUrl": url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
 
