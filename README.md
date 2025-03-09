# Criminal Identification with Surveillance Camera

![Criminal Detection](https://via.placeholder.com/800x400?text=Criminal+Detection+System)

## Overview
This project enhances law enforcement capabilities by using advanced facial recognition technology to identify and apprehend criminals in real-time from surveillance camera footage. It integrates MongoDB for secure data storage and Twilio API for instant alert notifications to authorities.

## Features
- 🔍 **Real-time Criminal Detection**: Uses facial recognition to match detected faces with stored criminal records.
- 📡 **Automated Alerts**: Sends SMS notifications to authorities using Twilio API when a criminal is detected.
- 🗂 **Secure Database**: Stores criminal details and encoded facial features in MongoDB.
- 📌 **Location Tracking**: Captures the detected criminal's location and shares it via Google Maps.

## Technology Stack
![Tech Stack](https://via.placeholder.com/800x200?text=Python+%7C+MongoDB+%7C+Twilio+API+%7C+OpenCV+%7C+Face_Recognition+%7C+Tkinter)

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

## Screenshots
### 🔍 Criminal Detection in Action
![Face Recognition](https://via.placeholder.com/800x400?text=Face+Recognition+in+Surveillance)

### 📋 Add Criminal Details
![Add Criminal UI](https://via.placeholder.com/800x400?text=Add+Criminal+Details+UI)

### 📡 Twilio Alert Message
![Twilio SMS Alert](https://via.placeholder.com/800x400?text=Twilio+Alert+Message+Example)

## Future Enhancements
- 📹 **Multi-Camera Support**: Extend detection to multiple surveillance cameras simultaneously.
- 🧠 **AI-based Prediction**: Implement AI models to predict criminal activities based on behavior.
- 📲 **Mobile App Integration**: Provide a mobile interface for law enforcement officers.

## Contributors
- **[Your Name]** - Developer

## License
This project is licensed under the MIT License.

📧 **Contact**: your.email@example.com | 🌍 **Website**: [YourWebsite.com](https://yourwebsite.com)

