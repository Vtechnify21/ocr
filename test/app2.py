
from flask import Flask, render_template, request, redirect
import os
import pytesseract
from PIL import Image
import cv2
import re
import fitz
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf'}

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced_img = cv2.equalizeHist(gray)
    return enhanced_img

def extract_aadhar_number(text):
    number_pattern = r'(\d{4} \d{4} \d{4})'
    number_match = re.search(number_pattern, text)
    number = number_match.group(1) if number_match else "Number not found"
    return number

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count
    for page_num in range(num_pages):
        page = pdf_document[page_num]
        extracted_text += page.get_text()
    pdf_document.close()
    return extracted_text

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    preprocessed_img = preprocess_image(image_path)
    img = Image.fromarray(preprocessed_img)
    extracted_text = pytesseract.image_to_string(img)
    aadhar_number = extract_aadhar_number(extracted_text)
    return extracted_text, aadhar_number

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if file.filename.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file_path)
            else:
                extracted_text, aadhar_number = extract_text_from_image(file_path)

            return render_template('result.html', extracted_text=extracted_text, aadhar_number=aadhar_number)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
