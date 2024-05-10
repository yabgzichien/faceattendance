import tkinter as tk
import utils
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
import json
import face_recognition
import requests
import datetime as date
import time

class App:
    def __init__(self):
        self.db_dir = './face_database'
        self.known_face_encoding = []
        self.known_face_name = []

        for image in os.listdir(self.db_dir):
            if (image.endswith('.jpg')):
                known_image = face_recognition.load_image_file(os.path.join("face_database" ,image))
                my_encoding = face_recognition.face_encodings(known_image)[0]
                self.known_face_encoding.append(my_encoding)
                self.known_face_name.append(image)

        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")


        self.checkIn_btn = utils.get_button(self.main_window, 'CheckIn', 'blue', self.checkIn)
        self.checkIn_btn.place(x=750, y=200)

        self.checkOut_btn = utils.get_button(self.main_window, 'CheckOut', 'red', self.checkout)
        self.checkOut_btn.place(x=750, y=300)

        self.register_main_btn = utils.get_button(self.main_window, 'Add', 'black', self.register)
        self.register_main_btn.place(x=750, y=400)

        self.webcam_label = utils.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y= 0, width=700, height=500)
        self.add_webcam(self.webcam_label)

        # database later change to a firebase database
        


    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)
        
        self.label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        self.recent_capture = frame

        imgS = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        self.rgb_imgS = imgS[:, :, ::-1]
        self.face_locations = face_recognition.face_locations(self.rgb_imgS)
        for (top, right, bottom, left) in self.face_locations:
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(self.recent_capture, (left, top), (right, bottom), (0, 0, 255), 3)



        img = cv2.cvtColor(self.recent_capture, cv2.COLOR_BGR2RGB)
        self.recent_pil = Image.fromarray(img)

        imgtk = ImageTk.PhotoImage(image=self.recent_pil)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)


        self.label.after(10, self.process_webcam)

    def checkIn(self):
        self.face_locations = face_recognition.face_locations(self.rgb_imgS)
        self.face_encodings = face_recognition.face_encodings(self.rgb_imgS, self.face_locations)

        for encoding in self.face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encoding, encoding)       
            face_distance = face_recognition.face_distance(self.known_face_encoding, encoding)
            best_index = np.argmin(face_distance)
            if(matches[best_index]):
                name = self.known_face_name[best_index]
                print(name)
                d = date.datetime.now()
                d = time.mktime(d.timetuple())
                obj = {"name": name, "checkIn" : d}
                headers = {"Content-type": "application/json"}
                requests.post('http://localhost:5000/checkIn', json=obj, headers=headers)
            else: 
                print("There is no nigga")


    def checkout(self):
        self.face_locations = face_recognition.face_locations(self.rgb_imgS)
        self.face_encodings = face_recognition.face_encodings(self.rgb_imgS, self.face_locations)

        for encoding in self.face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encoding, encoding)       
            face_distance = face_recognition.face_distance(self.known_face_encoding, encoding)
            best_index = np.argmin(face_distance)
            if(matches[best_index]):
                name = self.known_face_name[best_index]
                print(name)
                d = date.datetime.now()
                d = time.mktime(d.timetuple())
                obj = {"name": name, "checkout" : d}
                headers = {"Content-type": "application/json"}
                requests.post('http://localhost:5000/checkout', json=obj, headers=headers)
            else: 
                print("There is no nigga")


        
               

    def register(self):
        self.register_window = tk.Toplevel(self.main_window)
        self.register_window.geometry("1200x520+350+100")

        self.registered_btn = utils.get_button(self.register_window, 'Confirm', 'green', self.registered_successful)
        self.retry_btn = utils.get_button(self.register_window, 'Retry', 'Red', self.retry)
        self.registered_btn.place(x=750, y=300)
        self.retry_btn.place(x=750, y=400)

        self.image_label = utils.get_img_label(self.register_window)
        self.image_label.place(x=10, y=0, width=700, height=500)

        self.add_img(self.image_label)

        self.input = utils.get_entry_text(self.register_window)
        self.input.place(x=750, y=150)

        self.input_text = utils.get_text_label(self.register_window, "What's up nigga")
        self.input_text.place(x=750, y=50)

    
    def add_img(self, label):
        imgtk = ImageTk.PhotoImage(image=self.recent_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        # save into database
        self.register_new_capture = self.recent_capture.copy()

    
    def registered_successful(self):
        name = self.input.get(1.0, "end-1c")
        
        cv2.imwrite(os.path.join(self.db_dir, f'{name}.jpg'), self.register_new_capture)

        known_image = face_recognition.load_image_file(os.path.join("face_database" ,f"{name}.jpg"))
        my_encoding = face_recognition.face_encodings(known_image)[0]
        self.known_face_encoding.append(my_encoding)
        self.known_face_name.append(name)

        utils.msg_box('', 'User was registered')
        self.register_window.destroy()

    def retry(self):
        self.register_window.destroy()

    def start(self):   
        self.main_window.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()