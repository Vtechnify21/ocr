from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    # Load the image using PIL
    img = Image.open(image_path)
    
    # Perform OCR to extract text from the image
    extracted_text = pytesseract.image_to_string(img)
    #custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789 --tessdata-dir "<path_to_tessdata>"'
    #extracted_text = pytesseract.image_to_string(img, config=custom_config)
    
    return extracted_text

#def extract_information_from_text(text):
    # Placeholder logic for extracting date, number, and sex from text
    # You'll need to adapt this to your actual use case
   # date = "2023-08-10"  # Replace with extracted date
    #number = "1234567890"  # Replace with extracted number
   # sex = "Male"  # Replace with extracted sex
    
 #   return date, number, sex

def extract_information_from_text(text):
    # Example regular expressions to extract date, number, and sex
    import re

    # Date extraction (assuming format: DD/MM/YYYY)
    date_pattern = r'(\d{2}/\d{2}/\d{4})'
    date_match = re.search(date_pattern, text)
    date = date_match.group(1) if date_match else "Date not found"


    # Sex extraction (assuming "Male" or "Female" appears in the text)
    sex_pattern = r'(Male|Female)'
    sex_match = re.search(sex_pattern, text, re.IGNORECASE)
    sex = sex_match.group(1) if sex_match else "Sex not found"


    # Number extraction (assuming it's a 10-digit number)
    number_pattern = r'(\d{12})'
    number_match = re.search(number_pattern, text)
    number = number_match.group(1) if number_match else "Number not found"
    
    return date, number, sex




@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)

            extracted_text = extract_text_from_image(image_path)
            date, number, sex = extract_information_from_text(extracted_text)

            return render_template('result.html', 
                                   extracted_text=extracted_text, 
                                   date=date, number=number, sex=sex)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
