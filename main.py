from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    try:
        return JSONResponse(content={"imageUrl"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
