# Medical Report Analyzer

A web application that provides medical report analysis, symptoms analysis, and medicine information using AI. The application supports both English and Bengali (বাংলা) languages.

## Features

1. **Medical Report Analysis**
   - Upload medical reports (JPG, PDF)
   - Extract and analyze test results
   - Get health insights and suggestions

2. **Symptoms Analysis**
   - Describe symptoms in detail
   - Get potential conditions and urgency level
   - Receive immediate steps and precautions

3. **Medicine Information**
   - Get detailed medicine analysis
   - View usage, side effects, and precautions
   - Personalized information based on age and gender
   - Dosage schedule analysis

4. **Bilingual Support**
   - Toggle between English and Bengali
   - Instant translation of analysis results

## Technologies Used

- Python/Flask (Backend)
- JavaScript/HTML/CSS (Frontend)
- Tailwind CSS (Styling)
- Ollama with deepseek-r1:14b model (AI Analysis)
- Tesseract OCR (Text Extraction)
- Google Translate API (Translation)

## Prerequisites

1. Python 3.8 or higher
2. Tesseract OCR installed
3. Ollama with deepseek-r1:14b model

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd medical-report-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
   - Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`

5. Install and run Ollama:
   - Follow instructions at [Ollama](https://ollama.ai)
   - Pull the model: `ollama pull deepseek-r1:14b`

## Configuration

1. Set Tesseract path in `app.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path as needed
```

2. Ensure Ollama is running with the deepseek-r1:14b model:
```bash
ollama run deepseek-r1:14b
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Analyzing Medical Reports**
   - Click "Report Analysis" tab
   - Upload JPG or PDF file
   - View analysis results
   - Optionally translate to Bengali

2. **Analyzing Symptoms**
   - Click "Symptoms Analysis" tab
   - Describe symptoms in detail
   - Click "Analyze Symptoms"
   - View analysis and recommendations

3. **Getting Medicine Information**
   - Click "Medicine Info" tab
   - Enter patient age and gender
   - Input medicine name and dosage schedule
   - Click "Analyze Medicine"
   - View detailed medicine analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 