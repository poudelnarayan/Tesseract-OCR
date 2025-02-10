from fastapi import FastAPI, File, UploadFile
import pytesseract
from PIL import Image
import shutil
import os

app = FastAPI()

# Set Tesseract path (inside Docker)
TESSERACT_PATH = "/usr/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded image
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Open and process image with Tesseract
        img = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(img)

        # Log extracted text
        print(f"Extracted Text: {extracted_text}")

        return {"message": "OCR successful", "extracted_text": extracted_text}
    except Exception as e:
        return {"error": str(e)}

# Run FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
