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


def extract_information(text):
    """
    Extracts structured information from noisy OCR text.
    """
    # Normalize text (remove extra spaces & new lines)
    text = re.sub(r'\s+', ' ', text).strip()

    # Extract License Number (DOL Number) - Handles numbers with dashes
    license_number_match = re.search(
        r"License\s*(No)?[:;]?\s*([\d-]+)", text, re.IGNORECASE)
    license_number = license_number_match.group(
        2) if license_number_match else "Not Found"

    # Extract Full Name - Ensures capitalization handling
    name_match = re.search(r"Name\s*[:;]?\s*([A-Z\s]+)", text)
    full_name = name_match.group(1).strip() if name_match else "Not Found"

    # Extract First and Last Name (Splitting on space)
    name_parts = full_name.split()
    first_name = name_parts[0].capitalize() if len(
        name_parts) > 0 else "Not Found"
    last_name = name_parts[-1].capitalize() if len(name_parts) > 1 else "Not Found"

    # Extract Father's Name - Handles OCR distortions like '| axman' → 'Laxman'
    father_name_match = re.search(
        r"F[/H]*\s*Name\s*[:;]?\s*([\w\s]+)", text, re.IGNORECASE)
    father_name = father_name_match.group(1).strip().replace(
        '|', 'L') if father_name_match else "Not Found"

    # Extract Citizenship Number - Matches patterns with errors in spaces
    citizenship_match = re.search(
        r"Citizenship\s*No\.?\s*[:;]?\s*([\d-]+)", text, re.IGNORECASE)
    citizenship_number = citizenship_match.group(
        1) if citizenship_match else "Not Found"

    # Extract Address - Allows errors in spacing & punctuation
    address_match = re.search(
        r"Address\s*[:;]?\s*([\w\s,-]+)", text, re.IGNORECASE)
    address = address_match.group(1).strip().replace(
        " ,", ",") if address_match else "Not Found"

    # Extract Date of Birth (DOB) - Handles variations like "D.O:2, 28-07-2002"
    dob_match = re.search(r"D\.?O\.?[:;,]?\s*([0-9-./]+)", text, re.IGNORECASE)
    dob = dob_match.group(1) if dob_match else "Not Found"

    # Return structured extracted data
    return {
        "License Number": license_number,
        "First Name": first_name,
        "Last Name": last_name,
        "Father's Name": father_name,
        "Citizenship Number": citizenship_number,
        "Address": address,
        "Date of Birth": dob,
    }


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
        extracted_data = extract_information(extracted_text)

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
