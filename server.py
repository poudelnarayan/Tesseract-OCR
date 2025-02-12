from fastapi import FastAPI, File, UploadFile
import pytesseract
from PIL import Image
import shutil
import os
import re

app = FastAPI()

# Set Tesseract path (inside Docker)
TESSERACT_PATH = "/usr/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_kyc_info(text):
    # Initialize a dictionary to hold the extracted information
    extracted_info = {}

    # Extract the name
    name_match = re.search(r"Name:\s*([\w\s]+)\n", text)
    if name_match:
        extracted_info['Name'] = name_match.group(1).strip()

    # Extract the address
    address_match = re.search(r"Address:\s*([\w\s,\-]+)\n", text)
    if address_match:
        extracted_info['Address'] = address_match.group(1).strip()

    # Extract the date of birth
    dob_match = re.search(r"D\.O:\)\s*(\d{2}\.\d{2}\-\d{2}\-\d{4})", text)
    if dob_match:
        extracted_info['Date of Birth'] = dob_match.group(1).strip()

    # Extract the father's name
    father_name_match = re.search(r"F/H Name:\s*\|\s*([\w\s]+)\n", text)
    if father_name_match:
        extracted_info['Father\'s Name'] = father_name_match.group(1).strip()

    # Extract the citizenship number
    citizenship_number_match = re.search(
        r"Citizenship No\.\:\s*([\w\.\-]+)", text)
    if citizenship_number_match:
        extracted_info['Citizenship Number'] = citizenship_number_match.group(
            1).strip()

    # Extract the contact number
    contact_number_match = re.search(r"Contact No\:\s*([\d]+)\s*\|", text)
    if contact_number_match:
        extracted_info['Contact Number'] = contact_number_match.group(
            1).strip()

    return extracted_info


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
        # Extract structured data
        extracted_data = extract_kyc_info(extracted_text)

        return {
            "message": "OCR successful",
            "extracted_text": extracted_text,
            "structured_data": extracted_data
        }
    except Exception as e:
        return {"error": str(e)}

# Run FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
