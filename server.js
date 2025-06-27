const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const { PythonShell } = require('python-shell');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Database connection
const db = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME || 'heart_disease_prediction'
});

// Authentication middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.sendStatus(401);

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
};

// Routes

// User registration
app.post('/api/register', async (req, res) => {
    try {
        const { username, password, email } = req.body;
        const hashedPassword = await bcrypt.hash(password, 10);

        const query = 'INSERT INTO users (username, password, email) VALUES (?, ?, ?)';
        db.query(query, [username, hashedPassword, email], (err, results) => {
            if (err) {
                console.error('Registration error:', err);
                return res.status(500).json({ error: 'Registration failed' });
            }
            res.status(201).json({ message: 'User registered successfully' });
        });
    } catch (error) {
        res.status(500).json({ error: 'Registration failed' });
    }
});

// User login
app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;

    const query = 'SELECT * FROM users WHERE username = ?';
    db.query(query, [username], async (err, results) => {
        if (err || results.length === 0) {
            return res.status(401).json({ error: 'Authentication failed' });
        }

        const user = results[0];
        const validPassword = await bcrypt.compare(password, user.password);

        if (!validPassword) {
            return res.status(401).json({ error: 'Authentication failed' });
        }

        const token = jwt.sign({ id: user.id, username: user.username }, process.env.JWT_SECRET);
        res.json({ token });
    });
});

// Submit patient data for prediction
app.post('/api/predict', authenticateToken, (req, res) => {
    const patientData = req.body;
    const userId = req.user.id;

    // Save patient record
    const patientQuery = `
        INSERT INTO patient_records 
        (user_id, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.query(patientQuery, 
        [userId, patientData.age, patientData.sex, patientData.cp, patientData.trestbps,
         patientData.chol, patientData.fbs, patientData.restecg, patientData.thalach,
         patientData.exang, patientData.oldpeak, patientData.slope, patientData.ca,
         patientData.thal],
        (err, results) => {
            if (err) {
                console.error('Error saving patient record:', err);
                return res.status(500).json({ error: 'Failed to save patient record' });
            }

            const patientRecordId = results.insertId;

            // Run prediction using Python script
            let options = {
                mode: 'json',
                pythonPath: 'python',
                pythonOptions: ['-u'],
                scriptPath: '../src/main/python/models',
                args: [JSON.stringify(patientData)]
            };

            PythonShell.run('heart_disease_model.py', options, (err, results) => {
                if (err) {
                    console.error('Prediction error:', err);
                    return res.status(500).json({ error: 'Prediction failed' });
                }

                const predictions = results[0];

                // Save predictions
                Object.entries(predictions).forEach(([algorithm, result]) => {
                    const predictionQuery = `
                        INSERT INTO predictions 
                        (patient_record_id, algorithm_name, prediction_result, confidence_score)
                        VALUES (?, ?, ?, ?)
                    `;

                    db.query(predictionQuery, 
                        [patientRecordId, algorithm, result.prediction, result.probability],
                        (err) => {
                            if (err) {
                                console.error('Error saving prediction:', err);
                            }
                        }
                    );
                });

                res.json(predictions);
            });
        }
    );
});

// Get user's prediction history
app.get('/api/history', authenticateToken, (req, res) => {
    const query = `
        SELECT pr.*, p.algorithm_name, p.prediction_result, p.confidence_score
        FROM patient_records pr
        LEFT JOIN predictions p ON pr.id = p.patient_record_id
        WHERE pr.user_id = ?
        ORDER BY pr.created_at DESC
    `;

    db.query(query, [req.user.id], (err, results) => {
        if (err) {
            console.error('Error fetching history:', err);
            return res.status(500).json({ error: 'Failed to fetch history' });
        }
        res.json(results);
    });
});

// Generate report
app.post('/api/report', authenticateToken, (req, res) => {
    const { type, data } = req.body;
    
    const query = 'INSERT INTO reports (user_id, report_type, report_data) VALUES (?, ?, ?)';
    db.query(query, [req.user.id, type, JSON.stringify(data)], (err, results) => {
        if (err) {
            console.error('Error generating report:', err);
            return res.status(500).json({ error: 'Failed to generate report' });
        }
        res.json({ message: 'Report generated successfully', reportId: results.insertId });
    });
});

// Get user's reports
app.get('/api/reports', authenticateToken, (req, res) => {
    const query = 'SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC';
    db.query(query, [req.user.id], (err, results) => {
        if (err) {
            console.error('Error fetching reports:', err);
            return res.status(500).json({ error: 'Failed to fetch reports' });
        }
        res.json(results);
    });
});

// Start server
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
}); 