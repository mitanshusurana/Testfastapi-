from typing import Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

def process_gemstone_image(file: UploadFile) -> Image.Image:
    original = Image.open(io.BytesIO(file.file.read())).convert("RGBA")
    return original
def upload_to_r2(image: Image.Image, filename: str) -> str:
    return "https://pub-edd8f524b4784df1b5961ce0d431f767.r2.dev/{r2_key}"
@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    try:
        processed_image = process_gemstone_image(file)
        file_id = str(uuid.uuid4())
        url = upload_to_r2(processed_image, file_id)
        return JSONResponse(content={"imageUrl": url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
