from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import os
from werkzeug.utils import secure_filename

# Import your PyTorch disease model
from crop_disease_model import load_model, predict

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========================================
# LOAD MODELS
# ========================================

print("Loading models...")
crop_model = None
label_encoder = None
disease_model = None
idx_to_class = None

try:
    print("Loading crop prediction model...")
    with open('models/crop_rf.pkl', 'rb') as f:
        crop_model = pickle.load(f)
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    print("✓ Crop prediction model loaded!")
except Exception as e:
    print(f"⚠️  Crop model error: {e}")

try:
    print("Loading disease detection model...")
    disease_model, idx_to_class = load_model(
        model_path='models/crop_disease_cnn.pth',
        class_map_path='models/class_mapping.json'
    )
    print("✓ Disease detection model loaded!")
except Exception as e:
    print(f"⚠️  Disease model error: {e}")

if crop_model or disease_model:
    print("\n🎉 Ready to start!\n")
else:
    print("\n❌ No models loaded!\n")

# ========================================
# HELPER FUNCTIONS
# ========================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_recommendation(disease_name):
    disease_lower = disease_name.lower()
    
    recommendations = {
        'healthy': 'Great! Your plant appears healthy. Continue regular care.',
        'rust': 'Apply fungicide. Remove infected leaves. Improve air circulation.',
        'blight': 'Use copper-based fungicide. Remove affected leaves. Avoid overhead watering.',
        'spot': 'Apply fungicide. Remove affected leaves. Improve drainage.',
        'smut': 'Use resistant varieties. Apply fungicide preventively.',
        'bacterial': 'Remove infected plants. Use copper bactericide. Improve sanitation.',
    }
    
    for key, rec in recommendations.items():
        if key in disease_lower:
            return rec
    
    return 'Consult agricultural expert for treatment recommendations.'

# ========================================
# ROUTES
# ========================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    """Crop prediction endpoint - FIXED VERSION"""
    if not crop_model:
        return jsonify({
            'success': False,
            'error': 'Crop prediction model not available'
        }), 503
    
    try:
        data = request.get_json()
        
        # Validate all fields are present
        required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 
                          'humidity', 'ph', 'rainfall']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Extract and convert features
        try:
            features_dict = {
                'N': float(data['nitrogen']),
                'P': float(data['phosphorus']),
                'K': float(data['potassium']),
                'temperature': float(data['temperature']),
                'humidity': float(data['humidity']),
                'ph': float(data['ph']),
                'rainfall': float(data['rainfall'])
            }
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'error': f'Invalid numeric value in input: {str(e)}'
            }), 400
        
        # Create DataFrame with feature names (fixes the warning)
        features_df = pd.DataFrame([features_dict])
        
        # Predict
        prediction = crop_model.predict(features_df)
        crop_name = prediction[0]

        return jsonify({
            'success': True,
            'crop': crop_name.title()
        })
        
    except Exception as e:
        print(f"Crop prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """Disease detection endpoint"""
    if not disease_model:
        return jsonify({
            'success': False,
            'error': 'Disease detection model not available'
        }), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image uploaded'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Use PNG, JPG, or JPEG'
            }), 400
        
        # Save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Predict
        result = predict(filepath, disease_model, idx_to_class)
        
        disease_name = result['prediction']
        confidence = result['confidence']
        
        # Clean display name
        disease_display = disease_name.replace('_', ' ')
        recommendation = get_recommendation(disease_name)
        
        # Cleanup
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'disease': disease_display,
            'confidence': confidence,
            'recommendation': recommendation
        })
        
    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        print(f"Disease prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'models': {
            'crop': 'loaded' if crop_model else 'unavailable',
            'disease': 'loaded' if disease_model else 'unavailable'
        }
    })

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ========================================
# RUN APP
# ========================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌾 Krishi - Smart Agriculture Platform")
    print("="*50)
    print("\n🚀 Starting Flask server...")
    print("📍 Access: http://localhost:5001")
    print("📁 Templates: ../frontend/templates")
    print("📁 Static: ../frontend/static")
    print("\n💡 Press Ctrl+C to stop\n")
    
    # Run on port 5001
    app.run(debug=True, host='0.0.0.0', port=5001)