import os
import sys
import json
from flask import Flask, request, render_template, jsonify
from pypdf import PdfReader
from resume_parser import parse_resume  # Ensure this is the correct function name

# Configure the application
sys.path.insert(0, os.path.abspath(os.getcwd()))

UPLOAD_PATH = "data"
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    try:
        # Save the uploaded PDF file
        doc = request.files['pdf_doc']
        file_path = os.path.join(UPLOAD_PATH, "file.pdf")
        doc.save(file_path)
        
        # Read text from the PDF file
        data = _read_file_from_path(file_path)
        
        # Extract information using parse_resume
        extracted_data = parse_resume(data)  # Ensure this function is correctly defined
        
        # Handle case where parse_resume might return a dict
        if isinstance(extracted_data, dict):
            json_data = json.dumps(extracted_data)
        else:
            try:
                json_data = json.loads(extracted_data)
            except json.JSONDecodeError:
                print(f"Invalid JSON response: {extracted_data}")
                json_data = json.dumps({"error": "Invalid JSON response from model"})
        
        return render_template('index.html', data=json_data)
    
    except Exception as e:
        print(f"Error in /process route: {e}")
        return jsonify({"error": "Internal server error"}), 500

def _read_file_from_path(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Handle pages with no text
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""

if __name__ == "__main__":
    app.run(port=8000, debug=True)
