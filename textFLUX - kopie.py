import os
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import shutil
from pathlib import Path

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Image Processor")
        self.root.geometry("800x700")
        
        # Load product data
        self.load_products()
        
        # Get image files
        self.source_folder = 'new_product_images'
        self.target_folder = 'generated_images_products'
        
        # Create target folder if it doesn't exist
        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)
        
        # Get all image files (png, jpg, jpeg)
        self.image_files = [f for f in os.listdir(self.source_folder) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = 0
        
        # Create a dropdown with product names
        self.setup_ui()
        
        # Show the first image
        if self.image_files:
            self.show_current_image()
        else:
            self.display_label.config(text="No images found in the source folder")
    
    def load_products(self):
        try:
            with open('myProductList.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = data['productlist']
                
            # Create a list of product options for the dropdown
            self.product_options = []
            for index, product in enumerate(self.products, 1):
                # Format: "001: Product Name"
                self.product_options.append(f"{index:03d}: {product['name']}")
                
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            self.products = []
            self.product_options = []
    
    def setup_ui(self):
        # Frame for the image
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Label to display the image
        self.display_label = ttk.Label(self.image_frame)
        self.display_label.pack(fill=tk.BOTH, expand=True)
        
        # Frame for controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X)
        
        # Product selection
        ttk.Label(control_frame, text="Select Product:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Create a combobox with autocomplete
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(control_frame, textvariable=self.product_var, width=50)
        self.product_combo['values'] = self.product_options
        self.product_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Search as you type
        self.product_combo.bind('<KeyRelease>', self.filter_combo)
        
        # Current file info
        self.file_info = ttk.Label(control_frame, text="")
        self.file_info.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Progress info
        self.progress_info = ttk.Label(control_frame, text="")
        self.progress_info.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_current_image)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # Skip button
        self.skip_button = ttk.Button(button_frame, text="Skip", command=self.next_image)
        self.skip_button.pack(side=tk.LEFT, padx=10)
        
        # Previous button
        self.prev_button = ttk.Button(button_frame, text="Previous", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=10)
    
    def filter_combo(self, event):
        value = event.widget.get()
        if value == '':
            self.product_combo['values'] = self.product_options
        else:
            filtered = [item for item in self.product_options if value.lower() in item.lower()]
            self.product_combo['values'] = filtered
    
    def show_current_image(self):
        if 0 <= self.current_index < len(self.image_files):
            # Get current image file
            current_file = self.image_files[self.current_index]
            file_path = os.path.join(self.source_folder, current_file)
            
            # Update file info
            self.file_info.config(text=f"Current file: {current_file}")
            
            # Update progress info
            self.progress_info.config(text=f"Progress: {self.current_index + 1}/{len(self.image_files)}")
            
            # Open and resize image for display
            try:
                img = Image.open(file_path)
                
                # Calculate resize dimensions to fit in the window
                display_width = 600
                display_height = 400
                
                # Resize while maintaining aspect ratio
                img.thumbnail((display_width, display_height))
                
                # Convert to PhotoImage for Tkinter
                photo = ImageTk.PhotoImage(img)
                
                # Update the display label
                self.display_label.config(image=photo)
                self.display_label.image = photo  # Keep a reference to prevent garbage collection
                
            except Exception as e:
                self.display_label.config(text=f"Error loading image: {str(e)}")
                self.display_label.image = None
    
    def save_current_image(self):
        if not self.product_var.get():
            return
        
        try:
            # Parse the selected product
            selected = self.product_var.get()
            product_id = selected.split(':')[0].strip()
            product_name = selected.split(':', 1)[1].strip() if ':' in selected else selected
            
            # Clean product name for filename
            clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-')).strip()
            clean_name = clean_name.replace(' ', '_')
            
            # Create target filename
            target_filename = f"{product_id}_{clean_name}.jpg"
            target_path = os.path.join(self.target_folder, target_filename)
            
            # Get current image file
            current_file = self.image_files[self.current_index]
            source_path = os.path.join(self.source_folder, current_file)
            
            # Open, convert, and save the image
            img = Image.open(source_path)
            
            # Convert to RGB if it's RGBA (PNG with transparency)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize to 384x384 for consistency
            img = img.resize((384, 384), Image.Resampling.LANCZOS)
            
            # Save as JPG
            img.save(target_path, 'JPEG', quality=70, optimize=True)
            
            print(f"Saved: {target_filename}")
            
            # Move to next image
            self.next_image()
            
        except Exception as e:
            print(f"Error saving image: {str(e)}")
    
    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_current_image()
        else:
            self.display_label.config(text="No more images to process")
            self.display_label.image = None
    
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()