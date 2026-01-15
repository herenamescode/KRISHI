from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os
from werkzeug.utils import secure_filename

# Import your PyTorch disease model
from crop_disease_model import load_model, predict

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========================================
# LOAD MODELS AT STARTUP
# ========================================

print("Loading models...")

try:
    # Load crop prediction model (Random Forest)
    print("Loading crop prediction model...")
    with open('models/crop_rf.pkl', 'rb') as f:
        crop_model = pickle.load(f)
    
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    print("✓ Crop prediction model loaded!")
    
    # Load disease detection model (PyTorch CNN)
    print("Loading disease detection model...")
    disease_model, idx_to_class = load_model(
        model_path='models/crop_disease_cnn.pth',
        class_map_path='models/class_mapping.json'
    )
    print("✓ Disease detection model loaded!")
    
    print("\n🎉 All models loaded successfully!\n")
    
except Exception as e:
    print(f"❌ Error loading models: {e}")
    print("\nPlease make sure you have:")
    print("  1. models/crop_rf.pkl")
    print("  2. models/label_encoder.pkl")
    print("  3. models/crop_disease_cnn.pth")
    print("  4. models/class_mapping.json")
    print("  5. crop_disease_model.py in the same directory as app.py\n")

# ========================================
# HELPER FUNCTIONS
# ========================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_disease_recommendation(disease_name):
    """Get treatment recommendation based on disease name"""
    disease_lower = disease_name.lower()
    
    recommendations = {
        'healthy': 'Great! Your plant appears healthy. Continue with regular care and monitoring.',
        'rust': 'Apply fungicide treatment (e.g., mancozeb or copper-based). Remove infected leaves and improve air circulation around plants.',
        'blight': 'Use copper-based fungicide. Remove and destroy affected leaves. Avoid overhead watering and ensure proper plant spacing.',
        'spot': 'Apply appropriate fungicide. Remove affected leaves. Avoid water splash on leaves and improve drainage.',
        'smut': 'Use resistant varieties in future plantings. Apply fungicide as preventive measure. Remove and destroy infected parts.',
        'bacterial': 'Remove infected plants. Use copper-based bactericide. Avoid overhead irrigation and improve field sanitation.',
        'brown': 'Apply appropriate fungicide. Improve field drainage and avoid water stress. Use balanced fertilization.'
    }
    
    # Check for keywords in disease name
    for key, recommendation in recommendations.items():
        if key in disease_lower:
            return recommendation
    
    return 'Consult with a local agricultural expert for specific treatment recommendations. Remove affected parts and monitor closely.'

# ========================================
# ROUTES
# ========================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    """
    Predict the best crop based on soil and climate parameters
    
    Expected JSON input:
    {
        "nitrogen": float,
        "phosphorus": float,
        "potassium": float,
        "temperature": float,
        "humidity": float,
        "ph": float,
        "rainfall": float
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 
                          'humidity', 'ph', 'rainfall']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract features in the correct order
        features = np.array([[
            float(data['nitrogen']),
            float(data['phosphorus']),
            float(data['potassium']),
            float(data['temperature']),
            float(data['humidity']),
            float(data['ph']),
            float(data['rainfall'])
        ]])
        
        # Make prediction
        prediction = crop_model.predict(features)
        crop_name = label_encoder.inverse_transform(prediction)[0]
        
        return jsonify({
            'success': True,
            'crop': crop_name.title()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid input values: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """
    Predict plant disease from leaf image using PyTorch CNN
    
    Expected form data:
    - image: image file
    """
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image uploaded'
            }), 400
        
        file = request.files['image']
        
        # Validate file
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Please upload PNG, JPG, or JPEG'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Make prediction using your PyTorch model
        result = predict(filepath, disease_model, idx_to_class)
        
        disease_name = result['prediction']
        confidence = result['confidence']
        
        # Clean up disease name for display
        disease_display = disease_name.replace('_', ' ').replace('  ', ' - ')
        
        # Get recommendation
        recommendation = get_disease_recommendation(disease_name)
        
        # Clean up - remove uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'disease': disease_display,
            'confidence': confidence,
            'recommendation': recommendation
        })
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': 'Image file not found'
        }), 400
    except Exception as e:
        # Clean up file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Krishi API is running',
        'models': {
            'crop_prediction': 'loaded',
            'disease_detection': 'loaded'
        }
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ========================================
# RUN APPLICATION
# ========================================

if __name__ == '__main__':
    print("\n" + "="*79)
    print("KRISHI (Knowledge-driven Real-time Intelligent System for Harvest & Irrigation)")
    print("="*79)
    print("\nStarting Flask server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    # Run the app
    # Set debug=True for development, debug=False for production
    app.run(debug=True, host='0.0.0.0', port=5000)