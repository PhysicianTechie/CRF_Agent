# app/main.py

import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import PyPDF2
import docx

# 1) Import your new CRF logic function
from logic import calculate_crf_pages

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    # Show your upload form at the main page
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 2) Apply your logic depending on file type
    if filename.lower().endswith('.pdf'):
        num_pages = parse_pdf(file_path)
        
        # Example usage: pass page count & factor to your logic function
        crf_result = calculate_crf_pages(num_pages, 2.0)

        return jsonify({
            'message': f"PDF uploaded. Found {num_pages} pages.",
            'num_pages': num_pages,
            'crf': crf_result
        })

    elif filename.lower().endswith('.docx'):
        # This is just a text preview for .docx files
        word_text = parse_word(file_path)
        return jsonify({
            'message': "DOCX uploaded successfully.",
            'preview_text': word_text[:100]
        })
    else:
        return jsonify({
            'message': "File uploaded, but it's neither PDF nor DOCX."
        })

def parse_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)

def parse_word(docx_path):
    doc = docx.Document(docx_path)
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)

if __name__ == '__main__':
    app.run(debug=True)
