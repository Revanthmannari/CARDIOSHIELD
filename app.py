from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from models.heart_disease_model import HeartDiseasePredictor
import pandas as pd
import os
import sqlite3
import hashlib

# Get the absolute path for the database and static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'users.db')
STATIC_PATH = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, 
    static_folder=STATIC_PATH,
    static_url_path='/static',
    template_folder='webapp')

app.config['SECRET_KEY'] = 'your_secret_key_here'
predictor = HeartDiseasePredictor()

# Ensure static directory exists
os.makedirs(os.path.join(STATIC_PATH, 'images'), exist_ok=True)

# Database initialization
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     email TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        print(f"Database initialized at {DB_PATH}")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")

init_db()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('predict'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    if 'user' in session:
        return redirect(url_for('predict'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashed_password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user'] = email
            return jsonify({'message': 'Login successful'})
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/register', methods=['GET'])
def register():
    if 'user' in session:
        return redirect(url_for('predict'))
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                 (email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET'])
def predict_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('predict.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return jsonify({'error': 'Please login first'}), 401
        
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                          'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert data to correct types with error handling
        try:
            patient_data = {
                'age': int(data['age']),
                'sex': int(data['sex']),
                'cp': int(data['cp']),
                'trestbps': int(data['trestbps']),
                'chol': int(data['chol']),
                'fbs': int(data['fbs']),
                'restecg': int(data['restecg']),
                'thalach': int(data['thalach']),
                'exang': int(data['exang']),
                'oldpeak': float(data['oldpeak']),
                'slope': int(data['slope']),
                'ca': int(data['ca']),
                'thal': int(data['thal'])
            }
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
        
        # Create DataFrame from patient data
        df = pd.DataFrame([patient_data])
        
        # Get predictions from all models
        try:
            predictions = predictor.predict(df)
        except Exception as e:
            return jsonify({'error': f'Prediction error: {str(e)}'}), 500
        
        # Calculate average confidence
        total_confidence = sum(result['probability'] * 100 for result in predictions.values())
        avg_confidence = total_confidence / len(predictions)
        
        # Determine final risk level and interpretation
        final_risk = "High Risk" if avg_confidence >= 50 else "Low Risk"
        
        # Generate interpretation and recommendation with detailed reasons and prevention methods
        if avg_confidence >= 75:
            interpretation = "Strong indication of heart disease risk."
            recommendation = {
                "main": "Immediate medical consultation is advised.",
                "reasons": [
                    "High probability score across multiple prediction models",
                    "Your combination of risk factors indicates significant cardiovascular strain",
                    "Early intervention is critical to prevent serious complications"
                ],
                "prevention": [
                    "Schedule an appointment with a cardiologist as soon as possible",
                    "Monitor blood pressure and heart rate daily",
                    "Strictly adhere to any prescribed medications",
                    "Reduce sodium intake and follow a heart-healthy diet",
                    "Minimize physical and emotional stress",
                    "Consider cardiac rehabilitation programs if recommended by your doctor"
                ]
            }
        elif avg_confidence >= 50:
            interpretation = "Moderate indication of heart disease risk."
            recommendation = {
                "main": "Schedule regular check-ups with your healthcare provider.",
                "reasons": [
                    "Multiple risk factors are present in your profile",
                    "Your indicators suggest developing cardiovascular issues",
                    "Proactive management can prevent condition worsening"
                ],
                "prevention": [
                    "Schedule a thorough cardiovascular examination",
                    "Get regular cholesterol and blood pressure screenings",
                    "Limit saturated fats and increase heart-healthy foods",
                    "Engage in moderate exercise for 30 minutes daily",
                    "Maintain healthy weight through balanced nutrition",
                    "Practice stress reduction techniques like meditation"
                ]
            }
        elif avg_confidence >= 25:
            interpretation = "Low indication of heart disease risk."
            recommendation = {
                "main": "Maintain a healthy lifestyle and continue regular check-ups.",
                "reasons": [
                    "Some risk factors are present but at lower levels",
                    "Your cardiovascular health appears to be relatively stable",
                    "Preventive measures can further reduce your risk"
                ],
                "prevention": [
                    "Continue annual check-ups with your primary care physician",
                    "Monitor cholesterol and blood pressure every 6 months",
                    "Follow a Mediterranean or DASH diet rich in fruits and vegetables",
                    "Exercise regularly with a mix of cardio and strength training",
                    "Limit alcohol consumption and avoid tobacco products",
                    "Ensure adequate sleep (7-8 hours) and stress management"
                ]
            }
        else:
            interpretation = "Very low indication of heart disease risk."
            recommendation = {
                "main": "Continue maintaining healthy habits.",
                "reasons": [
                    "Your current indicators show minimal cardiovascular risk",
                    "Your lifestyle choices appear to be supporting heart health",
                    "Regular monitoring is still important for long-term health"
                ],
                "prevention": [
                    "Maintain annual wellness check-ups",
                    "Continue heart-healthy eating with plenty of whole foods",
                    "Stay physically active with regular exercise",
                    "Maintain social connections and mental well-being",
                    "Stay educated about heart health developments",
                    "Consider preventive screenings appropriate for your age and gender"
                ]
            }
        
        return jsonify({
            'predictions': predictions,
            'average_confidence': avg_confidence,
            'final_risk': final_risk,
            'interpretation': interpretation,
            'recommendation': recommendation
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') 