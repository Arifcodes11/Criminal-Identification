import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import gridfs
import face_recognition
import pymongo
import io
import numpy as np
import requests
from twilio.rest import Client
import math
import threading
import time


# Connecting to Mongo Database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["criminals"]
collection = db["criminals"]
phone_collection = db["phone_numbers"]
fs = gridfs.GridFS(db)


class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path):
        # Load images and create face encodings
        for image_path in images_path:
            img = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(img)[0]
            self.known_face_encodings.append(encoding)
            name = image_path.split("/")[-1].split(".")[0]
            self.known_face_names.append(name)
        print("Encoding images loaded")

    def detect_known_faces(self, frame):
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = small_frame[:, :, ::-1]  # Convert from BGR to RGB

        # Find all face locations and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for any known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names

sfr = SimpleFacerec()

# Function to retrieve the images from MongoDB and encode them
def encode_image_from_url(file_id):
    try:
        file = fs.get(file_id)
        if not file:
            print(f"No file found with the id {file_id}")
            return

        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))  

        image = image.convert("RGB")
        # Convert the image to a numpy array
        image_np = np.array(image)   

        # Find face locations and encodings
        face_locations = face_recognition.face_locations(image_np)
        face_encodings = face_recognition.face_encodings(image_np, face_locations)
        
        if len(face_encodings) > 0:
            return face_encodings
        else:
            print("No faces found in the image:", file_id)
            return None
    except Exception as e:
        print("Error processing image from", file_id, ":", e)
        return None

# Global variables
add_criminal_image_label = None
add_criminal_name = None
add_criminal_window=None
remove_criminal_window_name=None


#to upload details to mongoDB

def store_data_to_mongodb(name, Father, Mother,gender,DOB,bg,identify, image_path):
    try:
        # Read the image file
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Store the image in GridFS
        file_id = fs.put(image_data, filename=image_path.split('/')[-1])
        print(f"Image {image_path} stored in MongoDB with id: {file_id}")

        # Load the image using face_recognition
        image = face_recognition.load_image_file(image_path)
        # Get the face encodings
        face_encodings = face_recognition.face_encodings(image)

        if face_encodings:
            encoding = face_encodings[0]  # Take the first encoding found
            # Convert the encoding to a list for storage in MongoDB
            encoding_list = encoding.tolist()
            # Store the data along with the image encoding in the criminals collection
            data = {'name': name, 'Father': Father,'Mother':Mother ,'gender':gender,'DOB':DOB,'bg':bg,'identify':identify,'image_id': file_id,'encoding':encoding}
            collection.insert_one(data)
            print("Data stored in MongoDB")
            return True
        else:
            print("No faces found in the image")
            return False
    except Exception as e:
        print(f"Failed to store data: {e}")
        return False

def select_and_store_data(entries):
    name = entries["Name"].get()
    Father = entries["Father's Name"].get()
    Mother = entries["Mother's Name"].get()
    gender = Mother = entries["Gender"].get()
    DOB = entries["DOB (yyyy-mm-dd)"].get()
    bg = entries["Blood Group"].get()
    identify = entries["Identification Mark"].get()
    image_path = filedialog.askopenfilename()
    if name and Father and image_path and Mother and gender and bg and identify:
        # Dummy store function, replace with your MongoDB store function
        if True:  # Replace with actual store function check
            messagebox.showinfo("Success", "Data stored successfully!")
        else:
            messagebox.showerror("Error", "Failed to store data.")
    else:
        messagebox.showerror("Error", "Please fill in all the fields.")
    add_criminal_window.destroy()



def delete_image():
    name = remove_criminal_window_name.get()
    if not name:
        messagebox.showwarning("Input Error", "Please provide all details and an image.")
        return
    # Dummy delete function, replace with your MongoDB delete function
    if True:  # Replace with actual delete function check
        messagebox.showinfo("Success", "Criminal details deleted successfully.")
    else:
        messagebox.showerror("Error", "Failed to delete data.")
    open_remove_criminal.destroy()


# Function to get current location
def get_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        if data['status'] == 'success':
            return data['lat'], data['lon'], data['city'], data['country']
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to send SMS with criminal location and details
def send_sms(location, details):
    

    lat, lon, city, country = location
    google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    message_body = f"Criminal Detected: {details}\nCurrent Location: {city}, {country} (Latitude: {lat}, Longitude: {lon}).\nGoogle Maps Link: {google_maps_link}"

    try:
        # Retrieve phone numbers from the database
        phone_numbers = phone_collection.find({}, {"_id": 0, "phone": 1, "lat": 1, "lon": 1})

        # Calculate the nearest phone number
        nearest_phone_number = None
        min_distance = math.inf
        for phone_number in phone_numbers:
            phone_lat = phone_number["lat"]
            phone_lon = phone_number["lon"]
            distance = math.sqrt((lat - phone_lat) ** 2 + (lon - phone_lon) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_phone_number = phone_number["phone"]

        if nearest_phone_number:
            # Send SMS to the nearest phone number
            message = client.messages.create(
                body=message_body,
                from_='+13148876858', 
                to=nearest_phone_number
            )
            print(f"Message sent to {nearest_phone_number}: {message.sid}")
        else:
            print("No phone number found in the database.")
    except Exception as e:
        print(f"Error: {e}")

# Function to detect criminal using camera
def reset_detected_criminals():
    global detected_criminals
    while True:
        time.sleep(900)  # Sleep for 900 seconds (15 minutes)
        detected_criminals.clear()

def detect_criminal():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Cannot open camera. Please check if the camera is connected and accessible.")
        return

    global detected_criminals
    detected_criminals = set()

    # Start the timer thread to reset the set every 15 minutes
    reset_thread = threading.Thread(target=reset_detected_criminals, daemon=True)
    reset_thread.start()

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Frame Error", "Failed to capture frame from camera.")
            break

        face_locations, face_names = sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            # Writing Text above the frame
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            # Drawing the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
            
            if name not in detected_criminals:
                detected_criminals.add(name)
                criminal_details = f"Name: {name}"
                location = get_location()
                if location:
                    send_sms(location, criminal_details)

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

import tkinter as tk
from tkinter import messagebox


# Function to open window to add criminal details
def open_add_criminal_window():
    global add_criminal_window, entries
    add_criminal_window = tk.Toplevel()
    add_criminal_window.title("Add Criminal Details")
    add_criminal_window.geometry("800x600")
    add_criminal_window.config(bg='#34495e')  # Set background color


 

    # Frame for image and buttons
    left_frame = tk.Frame(add_criminal_window, bg='#2c3e50')
    left_frame.pack(side=tk.LEFT, padx=20, pady=20)

    # Dummy image
    img = Image.open("C:/Users/Admin/OneDrive/Desktop/web_develop/miniproject/crimi.jpg")
    img = img.resize((200, 200), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    profile_image_label = tk.Label(left_frame, image=img)
    profile_image_label.image = img
    profile_image_label.pack(pady=10)

    btn_select_images = tk.Button(left_frame, text="Select Images", command=lambda: select_and_store_data(entries), bg='#2980b9', fg='white')

    btn_select_images.pack(pady=5)

    # Frame for entry fields
    right_frame = tk.Frame(add_criminal_window, bg='#2c3e50')
    right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

    tk.Label(right_frame, text="Enter Details", bg='#2c3e50', fg='skyblue', font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

    fields = ["Name", "Father's Name", "Mother's Name", "Gender", "DOB (yyyy-mm-dd)", "Blood Group", "Identification Mark"]
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(right_frame, text=f"{field} *", bg='#2c3e50', fg='white').grid(row=i+1, column=0, sticky=tk.E, padx=5, pady=5)
        entry = tk.Entry(right_frame, width=40)
        entry.grid(row=i+1, column=1, padx=5, pady=5)
        entries[field] = entry

    # Submit button
    btn_submit = tk.Button(right_frame, text="Submit Details", command=lambda: select_and_store_data(entries), bg='#2980b9', fg='white')
    btn_submit.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

# Function to open window to remove criminal details
def open_remove_criminal_window():
    global remove_criminal_window_name, open_remove_criminal
    open_remove_criminal = tk.Toplevel()
    open_remove_criminal.title("Remove Criminal Details")
    open_remove_criminal.geometry("300x150")
    open_remove_criminal.config(bg='#34495e')  # Set background color

    tk.Label(open_remove_criminal, text="Name:", bg='#34495e', fg='white').pack(pady=5)
    remove_criminal_window_name = tk.Entry(open_remove_criminal)
    remove_criminal_window_name.pack(pady=5)

    tk.Button(open_remove_criminal, text="Delete", command=delete_image, bg='#e74c3c', fg='white').pack(pady=10)

# Main window
root = tk.Tk()
root.title("Criminal Detection System")
root.geometry("1500x1500")
root.config(bg='#2c3e50')  # Set background color

# Load the background image
background_image = Image.open("C:/Users/Admin/OneDrive/Desktop/web_develop/miniproject/mini.jpg")
background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas to hold the background image
canvas = tk.Canvas(root, width=background_image.width, height=background_image.height)
canvas.pack(fill="both", expand=True)

# Display the background image
canvas.create_image(0, 0, image=background_photo, anchor="nw")

btn_style = {
    'bg': '#ff0000',
    'fg': 'white',
    'font': ('Helvetica', 12, 'bold'),
    'activebackground': '#FF0000',
    'activeforeground': 'white',
    'bd': 0,
    'relief': 'flat',
    'width': 20,
    'height': 2
}

btn_add = tk.Button(root, text="Add Criminal Details", command=open_add_criminal_window, **btn_style)
canvas.create_window(550, 190, anchor="nw", window=btn_add)

btn_remove = tk.Button(root, text="Remove Criminal Details", command=open_remove_criminal_window, **btn_style)
canvas.create_window(550, 270, anchor="nw", window=btn_remove)

btn_detect = tk.Button(root, text="Detect Criminal", command=detect_criminal, **btn_style)
canvas.create_window(550, 350, anchor="nw", window=btn_detect)

btn_exit = tk.Button(root, text="Exit", command=root.quit, **btn_style)
canvas.create_window(550, 430, anchor="nw", window=btn_exit)

root.mainloop()
