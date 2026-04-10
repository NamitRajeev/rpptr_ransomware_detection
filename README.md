# R.A.P.P.T.R. – Ransomware Anomaly Prediction, Prevention & Targeted Response

R.A.P.P.T.R. is a behavior-based ransomware detection system that leverages machine learning and system-level monitoring to identify suspicious and ransomware-like activity.

---

## Overview
This project focuses on detecting ransomware through **behavioral analysis** rather than traditional signature-based methods.

The system monitors process-level and system-level activity such as CPU usage, memory consumption, disk write operations, and process behavior.  
A hybrid detection pipeline combines:

- **Random Forest** for supervised classification of known patterns  
- **LSTM Autoencoder** for sequence-based anomaly detection  

The system produces a **process-level risk classification**:  
**Benign | Suspicious | Ransomware**

---

## Key Features
- Behavior-based ransomware detection  
- Hybrid ML approach (Random Forest + LSTM Autoencoder)  
- Sequence-based analysis using sliding window technique  
- System and process-level monitoring using `psutil`  
- Custom dataset generated using ransomware simulation scripts  
- Interactive dashboard for detection visualization and analysis  

---

## Technologies Used
- Python  
- scikit-learn  
- TensorFlow / Keras  
- psutil  
- pandas  
- NumPy  
- Streamlit (for dashboard visualization)  

---

## System Design
1. **Behavioral Monitoring**  
   Collects system and process-level metrics (CPU, memory, disk activity)

2. **Feature Engineering**  
   Aggregates data using sliding windows to capture temporal behavior

3. **Detection Layer**
   - Random Forest → supervised classification  
   - LSTM Autoencoder → anomaly detection via reconstruction error  

4. **Decision Layer**  
   Combines model outputs to classify behavior as benign, suspicious, or ransomware

---

## Project Scope
The system is evaluated in a **controlled environment** using simulated ransomware behavior.  
No real malware is executed.

This project focuses on **detection and analysis**, providing a foundation for future extensions such as real-time deployment and automated response mechanisms.

---

## Status
Final stable version developed for academic evaluation.

---

## Disclaimer
This project is intended for **educational and research purposes only**.  
All ransomware behavior is simulated in a safe and controlled environment.