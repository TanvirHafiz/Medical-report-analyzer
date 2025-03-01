import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from dotenv import load_dotenv
import magic
import requests
import json
from googletrans import Translator
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Ollama endpoint
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:14b"

# Initialize translator
translator = Translator()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except pytesseract.TesseractNotFoundError:
        return "Error: Tesseract is not installed or not found in PATH. Please ensure Tesseract is installed and the path is correctly set."
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_pdf(pdf_path):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
    except pytesseract.TesseractNotFoundError:
        return "Error: Tesseract is not installed or not found in PATH. Please ensure Tesseract is installed and the path is correctly set."
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def translate_to_bangla(text):
    """Translate text to Bangla while preserving formatting"""
    try:
        if not text:  # Handle None or empty string
            return "No text to translate"

        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():  # Skip empty paragraphs
                translated_paragraphs.append('')
                continue

            # Split paragraph into lines
            lines = paragraph.split('\n')
            translated_lines = []
            
            for line in lines:
                if line.strip():  # Only translate non-empty lines
                    try:
                        # Use Google Translate
                        translation = translator.translate(line, dest='bn')
                        translated_text = translation.text if translation and translation.text else line
                        translated_lines.append(translated_text)
                    except Exception as e:
                        print(f"Translation error for line '{line}': {str(e)}")
                        translated_lines.append(line)  # Keep original text if translation fails
                else:
                    translated_lines.append(line)  # Keep empty lines as is
            
            # Rejoin lines in the paragraph
            translated_paragraphs.append('\n'.join(translated_lines))
        
        # Rejoin paragraphs with double newlines
        return '\n\n'.join(translated_paragraphs)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation completely fails

def analyze_medical_report(text):
    try:
        # Get the analysis in English
        prompt = f"""You are a medical report analyzer. Your task is to:
1. Analyze the given medical test results
2. Provide a simple explanation of what each test result means for overall health
3. Provide practical health suggestions based on the results
4. Format your response in clear sections

Here is the medical report to analyze:

{text}"""

        data = {
            "model": "deepseek-r1:14b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }
        
        response = requests.post(OLLAMA_ENDPOINT, json=data)
        response.raise_for_status()
        
        result = response.json()
        english_analysis = result.get('response', 'No analysis generated')

        # Return only English version initially
        return {
            'english': english_analysis,
            'bangla': None  # Will be translated on demand
        }

    except requests.exceptions.RequestException as e:
        if 'Connection refused' in str(e):
            return {
                'success': False,
                'error': "Error: Cannot connect to Ollama. Please make sure Ollama is running locally with deepseek-r1:14b model (ollama run deepseek-r1:14b)"
            }
        return {
            'success': False,
            'error': f"Error analyzing report: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error analyzing report: {str(e)}"
        }

def analyze_symptoms(symptoms):
    try:
        prompt = f"""You are a medical advisor. Based on the following symptoms, please:
1. Analyze the symptoms and provide potential conditions
2. Rate the urgency level (Low/Medium/High)
3. Suggest immediate steps or precautions
4. Recommend when to seek professional medical help

Please note this is for informational purposes only and not a substitute for professional medical advice.

Symptoms:
{symptoms}"""

        data = {
            "model": "deepseek-r1:14b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }
        
        response = requests.post(OLLAMA_ENDPOINT, json=data)
        response.raise_for_status()
        
        result = response.json()
        english_analysis = result.get('response', 'No analysis generated')
        medline_info = "\n\nFor more detailed medical information, please visit: https://medlineplus.gov/"

        # Return only English version initially
        return {
            'english': english_analysis + medline_info,
            'bangla': None  # Will be translated on demand
        }

    except requests.exceptions.RequestException as e:
        if 'Connection refused' in str(e):
            return {
                'success': False,
                'error': "Error: Cannot connect to Ollama. Please make sure Ollama is running locally with deepseek-r1:14b model (ollama run deepseek-r1:14b)"
            }
        return {
            'success': False,
            'error': f"Error analyzing symptoms: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error analyzing symptoms: {str(e)}"
        }

def analyze_medicine(medicine_name, dosage, patient):
    try:
        # Format dosage string
        dosage_str = []
        if dosage['morning'] > 0:
            dosage_str.append(f"{dosage['morning']} tablet(s) in the morning")
        if dosage['evening'] > 0:
            dosage_str.append(f"{dosage['evening']} tablet(s) in the evening")
        if dosage['night'] > 0:
            dosage_str.append(f"{dosage['night']} tablet(s) at night")
        
        formatted_dosage = ", ".join(dosage_str)

        prompt = f"""You are a medical information advisor. Please analyze the following medicine and dosage for a specific patient:

Patient Information:
- Age: {patient['age']} years old
- Gender: {patient['gender']}

Medicine Name: {medicine_name}
Current Dosage: {formatted_dosage}

Please provide the following information, taking into account the patient's age and gender:
1. What is this medicine primarily used for? List all common uses.
2. What are the common side effects? List them from most common to severe, noting any specific concerns for this patient's age/gender group.
3. What is the manufacturer's recommended dosage? Compare with the current dosage and note any age/gender-specific dosing considerations.
4. Are there any specific precautions or warnings for this patient's demographic?
5. What drug interactions should be considered?
6. When should someone seek medical attention while taking this medicine?
7. Are there any special considerations or additional monitoring needed for this patient's age/gender group?

Base your analysis on reliable medical sources and standard pharmaceutical information. Include any relevant warnings or disclaimers."""

        data = {
            "model": "deepseek-r1:14b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }
        
        response = requests.post(OLLAMA_ENDPOINT, json=data)
        response.raise_for_status()
        
        result = response.json()
        english_analysis = result.get('response', 'No analysis generated')

        # Add reference to MedlinePlus
        english_analysis += "\n\nFor more detailed medical information, please visit: https://medlineplus.gov/druginformation.html"

        return {
            'english': english_analysis,
            'bangla': None  # Will be translated on demand
        }

    except requests.exceptions.RequestException as e:
        if 'Connection refused' in str(e):
            return {
                'success': False,
                'error': "Error: Cannot connect to Ollama. Please make sure Ollama is running locally with deepseek-r1:14b model (ollama run deepseek-r1:14b)"
            }
        return {
            'success': False,
            'error': f"Error analyzing medicine: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error analyzing medicine: {str(e)}"
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logger.info(f"File saved: {filepath}")

            try:
                # Detect file type using python-magic
                mime = magic.Magic(mime=True)
                file_type = mime.from_file(filepath)
                logger.info(f"Detected file type: {file_type}")
                
                # Extract text based on file type
                if 'pdf' in file_type.lower():
                    text = extract_text_from_pdf(filepath)
                elif 'image' in file_type.lower():
                    text = extract_text_from_image(filepath)
                else:
                    os.remove(filepath)
                    logger.error(f"Invalid file type: {file_type}")
                    return jsonify({'error': 'Invalid file type'}), 400

                # Clean up the uploaded file
                os.remove(filepath)
                logger.info("File processed and removed")

                # Analyze the extracted text
                logger.info("Starting text analysis")
                analysis = analyze_medical_report(text)
                logger.info("Analysis completed")
                
                if isinstance(analysis, dict) and 'error' in analysis:
                    return jsonify(analysis), 500
                
                return jsonify({
                    'success': True,
                    'analysis': analysis
                })
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500

        logger.error("Invalid file type from extension check")
        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        logger.error(f"Unexpected error in upload_file: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/analyze-symptoms', methods=['POST'])
def process_symptoms():
    try:
        data = request.get_json()
        if not data or 'symptoms' not in data:
            logger.error("No symptoms provided in request")
            return jsonify({'error': 'No symptoms provided'}), 400

        symptoms = data['symptoms']
        if not symptoms.strip():
            logger.error("Empty symptoms string provided")
            return jsonify({'error': 'Symptoms cannot be empty'}), 400

        logger.info("Starting symptoms analysis")
        analysis = analyze_symptoms(symptoms)
        logger.info("Symptoms analysis completed")
        
        if isinstance(analysis, dict) and 'error' in analysis:
            return jsonify(analysis), 500
            
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error in process_symptoms: {str(e)}")
        return jsonify({'error': f'Error processing symptoms: {str(e)}'}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            logger.error("No text provided for translation")
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        if not text.strip():
            logger.error("Empty text provided for translation")
            return jsonify({'error': 'Text cannot be empty'}), 400

        logger.info("Starting translation")
        translated_text = translate_to_bangla(text)
        logger.info("Translation completed")
        
        return jsonify({
            'success': True,
            'translation': translated_text
        })
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error during translation: {str(e)}'
        }), 500

@app.route('/analyze-medicine', methods=['POST'])
def process_medicine():
    try:
        data = request.get_json()
        if not data or 'medicine' not in data or 'dosage' not in data or 'patient' not in data:
            logger.error("Missing medicine information")
            return jsonify({'error': 'Missing required information'}), 400

        medicine = data['medicine'].strip()
        dosage = data['dosage']
        patient = data['patient']

        if not medicine:
            logger.error("Empty medicine name provided")
            return jsonify({'error': 'Medicine name cannot be empty'}), 400

        # Validate dosage format
        required_fields = ['morning', 'evening', 'night']
        if not all(field in dosage for field in required_fields):
            logger.error("Invalid dosage format")
            return jsonify({'error': 'Invalid dosage format'}), 400

        # Validate patient information
        if not isinstance(patient.get('age'), int) or patient['age'] <= 0:
            logger.error("Invalid patient age")
            return jsonify({'error': 'Invalid patient age'}), 400

        if not patient.get('gender') or patient['gender'] not in ['male', 'female', 'other']:
            logger.error("Invalid patient gender")
            return jsonify({'error': 'Invalid patient gender'}), 400

        logger.info(f"Starting medicine analysis for: {medicine} (Patient: {patient['age']}y, {patient['gender']})")
        analysis = analyze_medicine(medicine, dosage, patient)
        logger.info("Medicine analysis completed")
        
        if isinstance(analysis, dict) and 'error' in analysis:
            return jsonify(analysis), 500
            
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error in process_medicine: {str(e)}")
        return jsonify({'error': f'Error processing medicine information: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 