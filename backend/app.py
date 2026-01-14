from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


print("Loading models...")

try:
    
    with open('models/crop_rf.pkl', 'rb') as f:
        crop_model = pickle.load(f)
    
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    
    # Load disease detection models
    corn_model = load_model('models/corn_disease.h5')
    rice_model = load_model('models/rice_disease.h5')
    wheat_model = load_model('models/wheat_disease.h5')
    
    print("All models loaded successfully!")
    
except Exception as e:
    print(f"Error loading models: {e}")
    print("Please make sure all model files exist in the 'models' folder")

# Disease class labels (you'll need to update these based on your actual model classes)
DISEASE_CLASSES = {
    'corn': [
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust_',
        'Corn_(maize)___Northern_Leaf_Blight',
        'Corn_(maize)___healthy'
    ],
    'rice': [
        'Rice___Bacterial_leaf_blight',
        'Rice___Brown_spot',
        'Rice___Leaf_smut',
        'Rice___healthy'
    ],
    'wheat': [
        'Wheat___Brown_rust',
        'Wheat___Yellow_rust',
        'Wheat___healthy'
    ]
}

# Disease recommendations (customize based on your needs)
DISEASE_RECOMMENDATIONS = {
    'healthy': 'Great! Your plant appears healthy. Continue with regular care and monitoring.',
    'rust': 'Apply fungicide treatment. Remove infected leaves and improve air circulation.',
    'blight': 'Use copper-based fungicide. Avoid overhead watering and space plants properly.',
    'spot': 'Apply appropriate fungicide. Remove affected leaves and avoid water splash on leaves.',
    'smut': 'Use resistant varieties in future plantings. Apply fungicide as preventive measure.'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_disease_recommendation(disease_name):
    """Get recommendation based on disease name"""
    disease_lower = disease_name.lower()
    
    if 'healthy' in disease_lower:
        return DISEASE_RECOMMENDATIONS['healthy']
    elif 'rust' in disease_lower:
        return DISEASE_RECOMMENDATIONS['rust']
    elif 'blight' in disease_lower:
        return DISEASE_RECOMMENDATIONS['blight']
    elif 'spot' in disease_lower:
        return DISEASE_RECOMMENDATIONS['spot']
     
    else:
        return 'Consult with a local agricultural expert for specific treatment recommendations.'

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
        
        # Extract features
        features = np.array([[
            data['nitrogen'],
            data['phosphorus'],
            data['potassium'],
            data['temperature'],
            data['humidity'],
            data['ph'],
            data['rainfall']
        ]])
        
        # Make prediction
        prediction = crop_model.predict(features)
        crop_name = label_encoder.inverse_transform(prediction)[0]
        
        return jsonify({
            'success': True,
            'crop': crop_name.title()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """
    Predict plant disease from leaf image
    
    Expected form data:
    - image: image file
    - crop_type: 'corn', 'rice', or 'wheat'
    """
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image uploaded'
            }), 400
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', 'corn')
        
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
        
        # Load and preprocess image
        img = image.load_img(filepath, target_size=(224, 224))  # Adjust size based on your model
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize
        
        # Select appropriate model
        if crop_type == 'corn':
            model = corn_model
            classes = DISEASE_CLASSES['corn']
        elif crop_type == 'rice':
            model = rice_model
            classes = DISEASE_CLASSES['rice']
        elif crop_type == 'wheat':
            model = wheat_model
            classes = DISEASE_CLASSES['wheat']
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid crop type'
            }), 400
        
        # Make prediction
        predictions = model.predict(img_array)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        disease_name = classes[predicted_class_idx]
        
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
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Krishi API is running'
    })

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static',
    static_url_path='/static'
)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

