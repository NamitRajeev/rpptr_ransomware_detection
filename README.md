# RPPTR – Ransomware Prediction, Prevention and Targeted Response

RPPTR is a behavior-based ransomware detection and containment system using machine learning and real-time process monitoring.

## Overview
This project detects ransomware-like behavior by monitoring process activity such as CPU usage and disk writes. A Random Forest model predicts malicious behavior, and a targeted response is performed by terminating the offending process.

## Key Features
- Behavior-based ransomware detection
- Machine learning–based prediction
- Real-time process monitoring
- Targeted process-level response
- Controlled ransomware simulation

## Technologies Used
- Python
- scikit-learn
- psutil
- pandas

## Project Scope
The system is evaluated in a controlled environment using simulated ransomware behavior. No real malware is executed.

## Status
Final stable version for academic evaluation.
