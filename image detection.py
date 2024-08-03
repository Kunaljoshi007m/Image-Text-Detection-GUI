import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import cv2
import easyocr
from PIL import Image, ImageTk


reader = easyocr.Reader(['en'])


media_path = ""
preprocess_option = "None"
zoom_factor = 1.0

def preprocess_image(image):
    global preprocess_option
    if preprocess_option == "Grayscale":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif preprocess_option == "Resize":
        width = int(image.shape[1] * 0.5)
        height = int(image.shape[0] * 0.5)
        return cv2.resize(image, (width, height))
    elif preprocess_option == "Contrast":
        return cv2.convertScaleAbs(image, alpha=1.5, beta=0)
    else:
        return image

def detect_text(image):
    results = reader.readtext(image)
    
    for (bbox, text, _) in results:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    return results

def update_image_display(image, window):
    global zoom_factor
    if image is None:
        return

    image = preprocess_image(image)
    height, width = image.shape[:2]
    new_size = (int(width * zoom_factor), int(height * zoom_factor))
    image = cv2.resize(image, new_size)
    
    results = detect_text(image)
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tk = ImageTk.PhotoImage(image_pil)
    
    image_label = ctk.CTkLabel(window, image=image_tk)
    image_label.image = image_tk
    image_label.pack()


    text = "\n".join([text for _, text, _ in results])
    with open('detected_text.txt', 'w') as f:
        f.write(text)
    messagebox.showinfo("Text Extraction", "Text has been saved to 'detected_text.txt'")

def upload_image():
    global media_path
    media_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if not media_path:
        return

    image = Image.open(media_path)
    image.thumbnail((400, 400))
    image_tk = ImageTk.PhotoImage(image)
    

    image_window = ctk.CTkToplevel(root)
    image_window.title("Uploaded Image")
    image_label = ctk.CTkLabel(image_window, image=image_tk)
    image_label.image = image_tk
    image_label.pack(pady=10)

def save_image():
    global media_path
    if not media_path:
        messagebox.showwarning("Warning", "Please upload an image first!")
        return

    image = cv2.imread(media_path)
    if image is None:
        messagebox.showerror("Error", "Error loading image!")
        return

    results = detect_text(image)
    
    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
    if save_path:
        cv2.imwrite(save_path, image)
        messagebox.showinfo("Save Image", f"Image saved as {save_path}")

def set_preprocess_option():
    global preprocess_option
    options = ["None", "Grayscale", "Resize", "Contrast"]
    # Use combobox for better option selection
    preprocess_window = ctk.CTkToplevel(root)
    preprocess_window.title("Set Preprocessing Option")
    preprocess_label = ctk.CTkLabel(preprocess_window, text="Choose preprocessing option:")
    preprocess_label.pack(pady=10)
    
    preprocess_combobox = ctk.CTkComboBox(preprocess_window, values=options)
    preprocess_combobox.set(preprocess_option)
    preprocess_combobox.pack(pady=10)
    
    def apply_option():
        selected_option = preprocess_combobox.get()
        if selected_option in options:
            preprocess_option = selected_option
            preprocess_window.destroy()
        else:
            messagebox.showwarning("Invalid Option", "Invalid preprocessing option selected. No preprocessing will be applied.")
    
    apply_button = ctk.CTkButton(preprocess_window, text="Apply", command=apply_option)
    apply_button.pack(pady=10)

def detect_text_window():
    global media_path
    if not media_path:
        messagebox.showwarning("No Image", "Please upload an image first!")
        return
    
    image = cv2.imread(media_path)
    if image is None:
        messagebox.showerror("Error", "Error loading image!")
        return
    
    detect_window = ctk.CTkToplevel(root)
    detect_window.title("Detected Text")
    update_image_display(image, detect_window)

def zoom_in():
    global zoom_factor
    if media_path:
        zoom_factor *= 1.1
        image = cv2.imread(media_path)
        zoom_in_window = ctk.CTkToplevel(root)
        zoom_in_window.title("Zoomed In Image")
        update_image_display(image, zoom_in_window)
    else:
        messagebox.showwarning("Zoom In", "No image uploaded for zooming in.")

def zoom_out():
    global zoom_factor
    if media_path:
        zoom_factor /= 1.1
        image = cv2.imread(media_path)
        zoom_out_window = ctk.CTkToplevel(root)
        zoom_out_window.title("Zoomed Out Image")
        update_image_display(image, zoom_out_window)
    else:
        messagebox.showwarning("Zoom Out", "No image uploaded for zooming out.")

root = ctk.CTk()
root.title("Image Text Detection GUI")
root.geometry("850x850")
ctk.set_appearance_mode("dark")


upload_button = ctk.CTkButton(root, text="Upload Image", command=upload_image, width=150, height=40)
upload_button.pack(pady=10)

detect_button = ctk.CTkButton(root, text="Detect Text", command=detect_text_window, width=150, height=40)
detect_button.pack(pady=10)

save_button = ctk.CTkButton(root, text="Save Image", command=save_image, width=150, height=40)
save_button.pack(pady=10)

preprocess_button = ctk.CTkButton(root, text="Set Preprocessing Option", command=set_preprocess_option, width=150, height=40)
preprocess_button.pack(pady=10)

zoom_in_button = ctk.CTkButton(root, text="Zoom In", command=zoom_in, width=150, height=40)
zoom_in_button.pack(pady=10)

zoom_out_button = ctk.CTkButton(root, text="Zoom Out", command=zoom_out, width=150, height=40)
zoom_out_button.pack(pady=10)

root.mainloop()
