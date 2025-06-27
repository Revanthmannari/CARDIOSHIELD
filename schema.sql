-- Create database
CREATE DATABASE IF NOT EXISTS heart_disease_prediction;
USE heart_disease_prediction;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create patient_records table
CREATE TABLE IF NOT EXISTS patient_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    age INT NOT NULL,
    sex ENUM('M', 'F') NOT NULL,
    cp TINYINT NOT NULL, -- chest pain type
    trestbps INT NOT NULL, -- resting blood pressure
    chol INT NOT NULL, -- serum cholesterol
    fbs BOOLEAN NOT NULL, -- fasting blood sugar
    restecg TINYINT NOT NULL, -- resting electrocardiographic results
    thalach INT NOT NULL, -- maximum heart rate achieved
    exang BOOLEAN NOT NULL, -- exercise induced angina
    oldpeak FLOAT NOT NULL, -- ST depression induced by exercise
    slope TINYINT NOT NULL, -- slope of the peak exercise ST segment
    ca TINYINT NOT NULL, -- number of major vessels colored by fluoroscopy
    thal TINYINT NOT NULL, -- thalassemia
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_record_id INT,
    algorithm_name VARCHAR(50) NOT NULL,
    prediction_result BOOLEAN NOT NULL,
    confidence_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_record_id) REFERENCES patient_records(id)
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    report_type VARCHAR(50) NOT NULL,
    report_data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX idx_patient_records_user_id ON patient_records(user_id);
CREATE INDEX idx_predictions_patient_record_id ON predictions(patient_record_id);
CREATE INDEX idx_reports_user_id ON reports(user_id); 