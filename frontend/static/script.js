// ========================================
// Smooth Scrolling for Navigation Links
// ========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ========================================
// Disease Detection Tab Switching
// ========================================
const tabButtons = document.querySelectorAll('.tab-btn');
const cropTypeInput = document.getElementById('cropType');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons
        tabButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to clicked button
        button.classList.add('active');
        
        // Update hidden input with selected crop type
        const cropType = button.getAttribute('data-crop');
        cropTypeInput.value = cropType;
        
        // Reset the form and results
        document.getElementById('diseaseForm').reset();
        document.getElementById('diseaseResult').style.display = 'none';
        document.getElementById('imagePreview').style.display = 'none';
        document.getElementById('uploadArea').querySelector('.upload-content').style.display = 'block';
    });
});

// ========================================
// Image Upload Handling
// ========================================
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('leafImage');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeImageBtn = document.getElementById('removeImage');
const uploadContent = uploadArea.querySelector('.upload-content');

// Click to upload
uploadArea.addEventListener('click', (e) => {
    if (e.target !== removeImageBtn && !e.target.closest('.remove-image')) {
        fileInput.click();
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect(file);
    }
});

// Handle file selection
function handleFileSelect(file) {
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadContent.style.display = 'none';
        imagePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// Remove image
removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.value = '';
    imagePreview.style.display = 'none';
    uploadContent.style.display = 'block';
    previewImg.src = '';
});

// ========================================
// Crop Prediction Form Submission
// ========================================
const cropForm = document.getElementById('cropForm');
const cropResult = document.getElementById('cropResult');
const cropResultText = document.getElementById('cropResultText');

cropForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous results
    cropResult.style.display = 'none';
    
    // Get form data
    const formData = {
        nitrogen: parseFloat(document.getElementById('nitrogen').value),
        phosphorus: parseFloat(document.getElementById('phosphorus').value),
        potassium: parseFloat(document.getElementById('potassium').value),
        temperature: parseFloat(document.getElementById('temperature').value),
        humidity: parseFloat(document.getElementById('humidity').value),
        ph: parseFloat(document.getElementById('ph').value),
        rainfall: parseFloat(document.getElementById('rainfall').value)
    };
    
    // Add loading state
    const submitBtn = cropForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<span>Analyzing...</span>';
    submitBtn.disabled = true;
    
    try {
        // Make API call to Flask backend
        const response = await fetch('/predict_crop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display result
            cropResultText.innerHTML = `
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌾</div>
                <strong>${data.crop}</strong>
                <p style="margin-top: 1rem; font-size: 1rem; color: var(--text-secondary);">
                    Based on your soil and climate conditions, this crop is recommended for optimal yield.
                </p>
            `;
            cropResult.style.display = 'block';
            
            // Scroll to result
            cropResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            alert('Error: ' + (data.error || 'Could not predict crop'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the server. Please make sure the Flask backend is running.');
    } finally {
        // Remove loading state
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;
    }
});

// ========================================
// Disease Detection Form Submission
// ========================================
const diseaseForm = document.getElementById('diseaseForm');
const diseaseResult = document.getElementById('diseaseResult');
const diseaseResultText = document.getElementById('diseaseResultText');
const diseaseConfidence = document.getElementById('diseaseConfidence');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceProgress = document.getElementById('confidenceProgress');

diseaseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous results
    diseaseResult.style.display = 'none';
    
    // Check if image is uploaded
    if (!fileInput.files[0]) {
        alert('Please upload an image first');
        return;
    }
    
    // Create FormData object
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('crop_type', cropTypeInput.value);
    
    // Add loading state
    const submitBtn = diseaseForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<span>Analyzing...</span>';
    submitBtn.disabled = true;
    
    try {
        // Make API call to Flask backend
        const response = await fetch('/predict_disease', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display result
            const diseaseEmoji = data.disease.toLowerCase().includes('healthy') ? '✅' : '⚠️';
            diseaseResultText.innerHTML = `
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">${diseaseEmoji}</div>
                <strong>${data.disease}</strong>
                ${data.recommendation ? `<p style="margin-top: 1rem; font-size: 1rem; color: var(--text-secondary); line-height: 1.6;">${data.recommendation}</p>` : ''}
            `;
            
            // Display confidence if available
            if (data.confidence !== undefined) {
                const confidencePercent = Math.round(data.confidence * 100);
                confidenceValue.textContent = confidencePercent + '%';
                confidenceProgress.style.width = confidencePercent + '%';
                diseaseConfidence.style.display = 'block';
            } else {
                diseaseConfidence.style.display = 'none';
            }
            
            diseaseResult.style.display = 'block';
            
            // Scroll to result
            diseaseResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            alert('Error: ' + (data.error || 'Could not detect disease'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the server. Please make sure the Flask backend is running.');
    } finally {
        // Remove loading state
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;
    }
});

// ========================================
// Intersection Observer for Animations
// ========================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards and sections
document.querySelectorAll('.card, .feature').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// ========================================
// Form Validation Helper
// ========================================
function validateNumberInput(input, min = null, max = null) {
    const value = parseFloat(input.value);
    
    if (isNaN(value)) {
        return false;
    }
    
    if (min !== null && value < min) {
        return false;
    }
    
    if (max !== null && value > max) {
        return false;
    }
    
    return true;
}

// Add real-time validation to number inputs
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', () => {
        if (input.value && !validateNumberInput(input, 0)) {
            input.style.borderColor = 'var(--error)';
        } else {
            input.style.borderColor = '';
        }
    });
});

// ========================================
// Console Welcome Message
// ========================================
console.log('%c🌾 Krishi - Smart Agriculture Platform', 'font-size: 20px; font-weight: bold; color: #2d5016;');
console.log('%cWelcome to Krishi! This platform uses AI to help farmers make better decisions.', 'font-size: 14px; color: #5a5a5a;');