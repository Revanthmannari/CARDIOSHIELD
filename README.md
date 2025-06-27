# CardioShield - Heart Disease Prediction System

CardioShield is a web-based application that uses machine learning to predict the likelihood of heart disease based on various medical parameters. The system employs multiple machine learning models to provide accurate predictions and risk assessments.

## Features

- **User Authentication**
  - Secure login and registration system
  - Password encryption using SHA-256
  - Session management

- **Heart Disease Prediction**
  - Comprehensive medical data input form
  - Multiple machine learning models:
    - Logistic Regression
    - Support Vector Machine (SVM)
    - Decision Tree
    - Random Forest
    - K-Nearest Neighbors (KNN)
  - Real-time prediction results
  - Risk level assessment
  - Detailed interpretation and recommendations

- **Modern UI/UX**
  - Responsive design using Bootstrap
  - Medical-themed interface
  - Interactive forms with validation
  - Real-time feedback

## Technical Stack

- **Backend**
  - Python 3.12
  - Flask web framework
  - SQLite database
  - Scikit-learn for machine learning models

- **Frontend**
  - HTML5
  - Bootstrap 5
  - JavaScript
  - Font Awesome icons

## Project Structure

```
src/main/python/
├── app.py                 # Main Flask application
├── users.db              # SQLite database for user management
├── models/               # Machine learning models
│   ├── heart_disease_model.py
│   └── models/          # Trained model files
├── webapp/              # HTML templates
│   ├── login.html
│   ├── register.html
│   └── predict.html
├── static/              # Static files
│   └── images/         # Medical illustrations
└── data/               # Dataset
    └── heart_disease_data.csv
```

## Setup Instructions

1. **Prerequisites**
   - Python 3.12 or higher
   - pip (Python package manager)

2. **Installation**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd [repository-name]

   # Install required packages
   pip install -r requirements.txt
   ```

3. **Running the Application**
   ```bash
   # Start the Flask server
   python src/main/python/app.py
   ```

4. **Accessing the Application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Register a new account or login
   - Start making predictions

## Usage Guide

1. **Registration/Login**
   - Create a new account using the registration page
   - Login with your credentials

2. **Making Predictions**
   - Fill in the medical parameters:
     - Age, Sex, Chest Pain Type
     - Blood Pressure, Cholesterol
     - Blood Sugar, ECG Results
     - Heart Rate, Exercise-Induced Angina
     - ST Depression, Slope
     - Number of Major Vessels, Thalassemia
   - Submit the form to get predictions
   - View detailed results and recommendations

## Security Features

- Password hashing using SHA-256
- Session-based authentication
- Input validation and sanitization
- Secure database storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset: UCI Heart Disease Dataset
- Icons: Font Awesome
- UI Framework: Bootstrap
- Machine Learning: Scikit-learn 