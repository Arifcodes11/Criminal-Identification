# Criminal Identification with Surveillance Camera

## Overview
This project enhances law enforcement capabilities by using advanced facial recognition technology to identify and apprehend criminals in real-time from surveillance camera footage. It integrates MongoDB for secure data storage and Twilio API for instant alert notifications to authorities.

## Features
- 🔍 **Real-time Criminal Detection**: Uses facial recognition to match detected faces with stored criminal records.
- 📡 **Automated Alerts**: Sends SMS notifications to authorities using Twilio API when a criminal is detected.
- 🗂 **Secure Database**: Stores criminal details and encoded facial features in MongoDB.
- 📌 **Location Tracking**: Captures the detected criminal's location and shares it via Google Maps.

## Technology Stack
- **Programming Language**: Python
- **Database**: MongoDB (GridFS for image storage)
- **APIs**: Twilio API for SMS notifications
- **Libraries**: OpenCV, Face_Recognition, Tkinter (GUI), GridFS

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/criminal-identification.git
cd criminal-identification

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## How It Works
1. 📷 **Capture**: The system continuously scans faces from live surveillance footage.
2. 🔎 **Identify**: Compares detected faces with the database of known criminals.
3. 🚨 **Alert**: If a match is found, an alert message with location details is sent via Twilio.
4. 📊 **Manage Database**: Admins can add or remove criminal records.

## Future Enhancements
- 📹 **Multi-Camera Support**: Extend detection to multiple surveillance cameras simultaneously.
- 🧠 **AI-based Prediction**: Implement AI models to predict criminal activities based on behavior.
- 📲 **Mobile App Integration**: Provide a mobile interface for law enforcement officers.

## Contributors
- **[Arif]** - Developer


