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


def extract_information(text):
    # Extract License Number (DOL Number)
    license_number_match = re.search(
        r"License\s*No\.?\s*[:;]?\s*([\w-]+)", text, re.IGNORECASE)
    license_number = license_number_match.group(
        1) if license_number_match else "Not Found"

    # Extract Name (Assuming "Name:" or similar pattern)
    name_match = re.search(r"Name\s*[:;]?\s*([A-Za-z\s]+)", text)
    full_name = name_match.group(1).strip() if name_match else "Not Found"

    # Split First and Last Name (Assuming the last word is the last name)
    name_parts = full_name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else "Not Found"
    last_name = name_parts[-1] if len(name_parts) > 1 else "Not Found"

    # Extract Father's Name
    father_name_match = re.search(
        r"F/H\s*Name\s*[:;]?\s*([A-Za-z\s]+)", text, re.IGNORECASE)
    father_name = father_name_match.group(
        1).strip() if father_name_match else "Not Found"

    # Extract Citizenship Number
    citizenship_match = re.search(
        r"Citizenship\s*No\.?\s*[:;]?\s*([\w-]+)", text, re.IGNORECASE)
    citizenship_number = citizenship_match.group(
        1) if citizenship_match else "Not Found"

    # Extract Address
    address_match = re.search(
        r"Address\s*[:;]?\s*([\w\s,]+)", text, re.IGNORECASE)
    address = address_match.group(1).strip() if address_match else "Not Found"

    # Extract Date of Birth (DOB) (Assuming D.O.B or D.O: or similar)
    dob_match = re.search(r"D\.?O\.?[:;]?\s*([0-9-./]+)", text, re.IGNORECASE)
    dob = dob_match.group(1) if dob_match else "Not Found"

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
