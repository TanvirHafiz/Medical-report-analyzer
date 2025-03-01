document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const reportTab = document.getElementById('report-tab');
    const symptomsTab = document.getElementById('symptoms-tab');
    const medicineTab = document.getElementById('medicine-tab');
    const reportSection = document.getElementById('report-section');
    const symptomsSection = document.getElementById('symptoms-section');
    const medicineSection = document.getElementById('medicine-section');
    const translateBtn = document.getElementById('translate-btn');
    let currentAnalysis = null;

    reportTab.addEventListener('click', () => {
        reportTab.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        symptomsTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        medicineTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        reportSection.classList.remove('hidden');
        symptomsSection.classList.add('hidden');
        medicineSection.classList.add('hidden');
    });

    symptomsTab.addEventListener('click', () => {
        symptomsTab.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        reportTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        medicineTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        symptomsSection.classList.remove('hidden');
        reportSection.classList.add('hidden');
        medicineSection.classList.add('hidden');
    });

    medicineTab.addEventListener('click', () => {
        medicineTab.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        reportTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        symptomsTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        medicineSection.classList.remove('hidden');
        reportSection.classList.add('hidden');
        symptomsSection.classList.add('hidden');
    });

    // File upload functionality
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const englishBtn = document.getElementById('english-btn');
    const banglaBtn = document.getElementById('bangla-btn');
    const englishContent = document.getElementById('english-content');
    const banglaContent = document.getElementById('bangla-content');

    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-blue-500');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (!file) return;

        // Check file type
        const allowedTypes = ['image/jpeg', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            showError('Please upload a JPG or PDF file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        showLoading();
        console.log('Uploading file:', file.name);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            handleResponse(data);
        })
        .catch(err => {
            console.error('Error:', err);
            handleError(err);
        });
    }

    // Symptoms analysis functionality
    const symptomsInput = document.getElementById('symptoms-input');
    const analyzeButton = document.getElementById('analyze-symptoms');

    analyzeButton.addEventListener('click', () => {
        const symptoms = symptomsInput.value.trim();
        if (!symptoms) {
            showError('Please describe your symptoms');
            return;
        }

        showLoading();
        console.log('Analyzing symptoms');

        fetch('/analyze-symptoms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms: symptoms })
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            handleResponse(data);
        })
        .catch(err => {
            console.error('Error:', err);
            handleError(err);
        });
    });

    // Medicine analysis functionality
    const medicineName = document.getElementById('medicine-name');
    const dosageMorning = document.getElementById('dosage-morning');
    const dosageEvening = document.getElementById('dosage-evening');
    const dosageNight = document.getElementById('dosage-night');
    const patientAge = document.getElementById('patient-age');
    const patientGender = document.getElementById('patient-gender');
    const analyzeMedicineBtn = document.getElementById('analyze-medicine');

    analyzeMedicineBtn.addEventListener('click', () => {
        const medicine = medicineName.value.trim();
        const age = patientAge.value.trim();
        const gender = patientGender.value;

        // Validate inputs
        if (!medicine) {
            showError('Please enter a medicine name');
            return;
        }

        if (!age) {
            showError('Please enter patient age');
            return;
        }

        if (!gender) {
            showError('Please select patient gender');
            return;
        }

        const dosage = {
            morning: parseInt(dosageMorning.value) || 0,
            evening: parseInt(dosageEvening.value) || 0,
            night: parseInt(dosageNight.value) || 0
        };

        if (dosage.morning === 0 && dosage.evening === 0 && dosage.night === 0) {
            showError('Please enter at least one dosage value');
            return;
        }

        showLoading();
        console.log('Analyzing medicine:', { medicine, age, gender, dosage });

        fetch('/analyze-medicine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                medicine: medicine,
                dosage: dosage,
                patient: {
                    age: parseInt(age),
                    gender: gender
                }
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            handleResponse(data);
        })
        .catch(err => {
            console.error('Error:', err);
            handleError(err);
        });
    });

    // Translation handling
    translateBtn.addEventListener('click', async () => {
        if (!currentAnalysis || !currentAnalysis.english) {
            showError('No content to translate');
            return;
        }

        // Show loading state
        translateBtn.disabled = true;
        translateBtn.textContent = 'Translating...';
        
        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: currentAnalysis.english })
            });

            const data = await response.json();
            
            if (data.success && data.translation) {
                // Store the translation
                currentAnalysis.bangla = data.translation;
                
                // Update the Bangla content
                try {
                    banglaContent.innerHTML = marked.parse(data.translation);
                } catch (err) {
                    console.error('Error parsing markdown:', err);
                    banglaContent.textContent = data.translation;
                }

                // Show Bangla button and hide translate button
                banglaBtn.classList.remove('hidden');
                translateBtn.classList.add('hidden');
                
                // Trigger Bangla view
                banglaBtn.click();
            } else {
                showError(data.error || 'Translation failed');
            }
        } catch (err) {
            console.error('Translation error:', err);
            showError('Failed to translate content');
        } finally {
            // Reset button state
            translateBtn.disabled = false;
            translateBtn.textContent = 'Translate to বাংলা';
        }
    });

    // Language switching
    englishBtn.addEventListener('click', () => {
        if (!currentAnalysis) return;
        
        englishBtn.classList.add('bg-blue-500', 'text-white');
        englishBtn.classList.remove('bg-gray-200', 'text-gray-700');
        banglaBtn.classList.add('bg-gray-200', 'text-gray-700');
        banglaBtn.classList.remove('bg-blue-500', 'text-white');
        englishContent.classList.remove('hidden');
        banglaContent.classList.add('hidden');
    });

    banglaBtn.addEventListener('click', () => {
        if (!currentAnalysis || !currentAnalysis.bangla) return;
        
        banglaBtn.classList.add('bg-blue-500', 'text-white');
        banglaBtn.classList.remove('bg-gray-200', 'text-gray-700');
        englishBtn.classList.add('bg-gray-200', 'text-gray-700');
        englishBtn.classList.remove('bg-blue-500', 'text-white');
        banglaContent.classList.remove('hidden');
        englishContent.classList.add('hidden');
    });

    function showLoading() {
        loading.classList.remove('hidden');
        result.classList.add('hidden');
        error.classList.add('hidden');
    }

    function handleResponse(data) {
        loading.classList.add('hidden');
        console.log('Handling response:', data);  // Debug log
        
        if (data.success && data.analysis) {
            currentAnalysis = data.analysis;  // Store the current analysis
            result.classList.remove('hidden');
            
            // Show English content
            try {
                console.log('English content:', currentAnalysis.english);  // Debug log
                englishContent.innerHTML = marked.parse(currentAnalysis.english);
            } catch (err) {
                console.error('Error parsing markdown:', err);
                englishContent.textContent = currentAnalysis.english;
            }

            // Show translate button, hide Bangla button if no translation yet
            translateBtn.classList.remove('hidden');
            banglaBtn.classList.add('hidden');
            
            // Show English view
            englishContent.classList.remove('hidden');
            banglaContent.classList.add('hidden');
            
            // Update button states
            englishBtn.classList.add('bg-blue-500', 'text-white');
            englishBtn.classList.remove('bg-gray-200', 'text-gray-700');
        } else {
            showError(data.error || 'An unexpected error occurred');
        }
    }

    function handleError(err) {
        console.error('Error details:', err);
        loading.classList.add('hidden');
        showError('An error occurred while processing your request. Please try again.');
    }

    function showError(message) {
        error.classList.remove('hidden');
        result.classList.add('hidden');
        errorMessage.textContent = message;
    }
}); 