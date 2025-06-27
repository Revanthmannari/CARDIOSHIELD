import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import json

class HeartDiseasePredictor:
    def __init__(self):
        self.models = {
            'logistic_regression': LogisticRegression(),
            'svm': SVC(probability=True),
            'decision_tree': DecisionTreeClassifier(),
            'random_forest': RandomForestClassifier(),
            'knn': KNeighborsClassifier()
        }
        self.scalers = {}
        
        # Get the absolute path to the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, 'models')
        self.data_path = os.path.join(current_dir, '..', 'data', 'heart_disease_data.csv')
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
            
        # Load or train models
        self.load_or_train_models()
        
    def load_or_train_models(self):
        """Load trained models if they exist, otherwise train new ones"""
        try:
            # Try to load the models
            for algorithm in self.models.keys():
                model_file = os.path.join(self.model_path, f'{algorithm}_model.joblib')
                scaler_file = os.path.join(self.model_path, f'{algorithm}_scaler.joblib')
                
                if os.path.exists(model_file) and os.path.exists(scaler_file):
                    self.models[algorithm] = joblib.load(model_file)
                    self.scalers[algorithm] = joblib.load(scaler_file)
                else:
                    raise FileNotFoundError("Model files not found")
                    
        except Exception as e:
            print(f"Training new models: {str(e)}")
            self.train_models()
            
    def train_models(self):
        """Train all models and save them"""
        # Load the dataset
        data = pd.read_csv(self.data_path)
        
        # Separate features and target
        X = data.drop('target', axis=1)
        y = data['target']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train and evaluate each model
        for algorithm, model in self.models.items():
            print(f"\nTraining {algorithm.replace('_', ' ').title()}...")
            
            # Scale the features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train the model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate the model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Perform cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            
            print(f"Accuracy: {accuracy:.2f}")
            print(f"Cross-validation scores: {cv_scores}")
            print(f"Mean CV score: {cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred))
            
            # Save the model and scaler
            joblib.dump(model, os.path.join(self.model_path, f'{algorithm}_model.joblib'))
            joblib.dump(scaler, os.path.join(self.model_path, f'{algorithm}_scaler.joblib'))
            
            self.scalers[algorithm] = scaler
            
    def predict(self, data):
        """Make predictions using all models"""
        predictions = {}
        
        for algorithm, model in self.models.items():
            # Scale the input data
            scaled_data = self.scalers[algorithm].transform(data)
            
            # Make prediction
            prediction = model.predict(scaled_data)[0]
            probability = model.predict_proba(scaled_data)[0][1]  # Probability of heart disease
            
            predictions[algorithm] = {
                'prediction': bool(prediction),
                'probability': float(probability)
            }
            
        return predictions

def get_user_input():
    """Get patient data from terminal input"""
    print("\n=== Heart Disease Risk Prediction ===")
    print("Please enter the following patient information:\n")
    
    data = {}
    
    # Age
    while True:
        try:
            data['age'] = int(input("Age: "))
            if 0 <= data['age'] <= 120:
                break
            print("Please enter a valid age between 0 and 120.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Sex
    while True:
        sex = input("Sex (M/F): ").upper()
        if sex in ['M', 'F']:
            data['sex'] = 1 if sex == 'M' else 0
            break
        print("Please enter 'M' for Male or 'F' for Female.")
    
    # Chest Pain Type
    while True:
        try:
            data['cp'] = int(input("Chest Pain Type (0-3):\n0: Typical angina\n1: Atypical angina\n2: Non-anginal pain\n3: Asymptomatic\nChoice: "))
            if 0 <= data['cp'] <= 3:
                break
            print("Please enter a number between 0 and 3.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Resting Blood Pressure
    while True:
        try:
            data['trestbps'] = int(input("Resting Blood Pressure (mm Hg): "))
            if 90 <= data['trestbps'] <= 200:
                break
            print("Please enter a valid blood pressure between 90 and 200.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Serum Cholesterol
    while True:
        try:
            data['chol'] = int(input("Serum Cholesterol (mg/dl): "))
            if 100 <= data['chol'] <= 600:
                break
            print("Please enter a valid cholesterol level between 100 and 600.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Fasting Blood Sugar
    while True:
        fbs = input("Fasting Blood Sugar > 120 mg/dl (Y/N): ").upper()
        if fbs in ['Y', 'N']:
            data['fbs'] = 1 if fbs == 'Y' else 0
            break
        print("Please enter 'Y' for Yes or 'N' for No.")
    
    # Resting ECG Results
    while True:
        try:
            data['restecg'] = int(input("Resting ECG Results (0-2):\n0: Normal\n1: ST-T wave abnormality\n2: Left ventricular hypertrophy\nChoice: "))
            if 0 <= data['restecg'] <= 2:
                break
            print("Please enter a number between 0 and 2.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Maximum Heart Rate
    while True:
        try:
            data['thalach'] = int(input("Maximum Heart Rate Achieved: "))
            if 60 <= data['thalach'] <= 202:
                break
            print("Please enter a valid heart rate between 60 and 202.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Exercise Induced Angina
    while True:
        exang = input("Exercise Induced Angina (Y/N): ").upper()
        if exang in ['Y', 'N']:
            data['exang'] = 1 if exang == 'Y' else 0
            break
        print("Please enter 'Y' for Yes or 'N' for No.")
    
    # ST Depression
    while True:
        try:
            data['oldpeak'] = float(input("ST Depression: "))
            if 0 <= data['oldpeak'] <= 6.2:
                break
            print("Please enter a valid ST depression value between 0 and 6.2.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Slope of Peak Exercise ST Segment
    while True:
        try:
            data['slope'] = int(input("Slope of Peak Exercise ST Segment (0-2):\n0: Upsloping\n1: Flat\n2: Downsloping\nChoice: "))
            if 0 <= data['slope'] <= 2:
                break
            print("Please enter a number between 0 and 2.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Number of Major Vessels
    while True:
        try:
            data['ca'] = int(input("Number of Major Vessels (0-3): "))
            if 0 <= data['ca'] <= 3:
                break
            print("Please enter a number between 0 and 3.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Thalassemia
    while True:
        try:
            data['thal'] = int(input("Thalassemia (1-3):\n1: Normal\n2: Fixed defect\n3: Reversible defect\nChoice: "))
            if 1 <= data['thal'] <= 3:
                break
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")
    
    return pd.DataFrame([data])

def main():
    predictor = HeartDiseasePredictor()
    
    while True:
        patient_data = get_user_input()
        predictions = predictor.predict(patient_data)
        
        print("\n=== Individual Model Predictions ===")
        total_confidence = 0
        num_models = len(predictions)
        
        for algorithm, result in predictions.items():
            confidence = result['probability'] * 100
            risk_level = "High Risk" if result['prediction'] else "Low Risk"
            total_confidence += confidence
            
            print(f"\n{algorithm.replace('_', ' ').title()}:")
            print(f"Risk Level: {risk_level}")
            print(f"Confidence: {confidence:.2f}%")
        
        # Calculate average confidence and final decision
        avg_confidence = total_confidence / num_models
        final_risk = "High Risk" if avg_confidence >= 50 else "Low Risk"
        
        print("\n=== Final Analysis ===")
        print(f"Average Confidence: {avg_confidence:.2f}%")
        print(f"Overall Risk Level: {final_risk}")
        
        # Print detailed interpretation
        print("\n=== Interpretation ===")
        if avg_confidence >= 75:
            print("Strong indication of heart disease risk.")
            print("Recommendation: Immediate medical consultation is advised.")
        elif avg_confidence >= 50:
            print("Moderate indication of heart disease risk.")
            print("Recommendation: Schedule regular check-ups with your healthcare provider.")
        elif avg_confidence >= 25:
            print("Low indication of heart disease risk.")
            print("Recommendation: Maintain a healthy lifestyle and continue regular check-ups.")
        else:
            print("Very low indication of heart disease risk.")
            print("Recommendation: Continue maintaining healthy habits.")
        
        # Ask for another prediction
        while True:
            again = input("\nWould you like to make another prediction? (Y/N): ").upper()
            if again in ['Y', 'N']:
                break
            print("Please enter 'Y' for Yes or 'N' for No.")
        
        if again == 'N':
            break
    
    print("\nThank you for using the Heart Disease Prediction System!")

if __name__ == "__main__":
    main() 