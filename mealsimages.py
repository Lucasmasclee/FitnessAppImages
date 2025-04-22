import os
import json
from time import sleep
import requests
from PIL import Image
from io import BytesIO
import base64
import shutil
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk
import webbrowser
import tempfile


# Initialize the Stability AI API key
STABILITY_API_KEY = "sk-nBtYGbuaBVPBOuwrMoflXG9GdV4nDBJ7VuY4R6QjzM5XaPPz"  # Replace with your actual key
STABILITY_API_HOST = "https://api.stability.ai"


def create_direct_prompt(product):
    """Create a standardized prompt for consistent product photography"""
    name = product['name']
    
    # Get ingredients list if available
    ingredients_list = product.get('ingredients', [])
    ingredients_text = ""
    if ingredients_list:
        ingredients_text = f" containing {', '.join(ingredients_list)}"
    
    prompt = (
        f"Ultra-realistic product photography of a single {name}{ingredients_text} on a pure white background. "
        f"The {name} should take up exactly 70% of the frame and be perfectly centered. "
        f"Shot directly from the front or top (whichever best shows the product), "
        f"with professional studio lighting. The {name} must be in its natural orientation "
        f"(not upside down). Style reference: stock photography for grocery stores. "
        f"Photorealistic, not artistic. The image must be clean, simple, and consistent "
        f"with standardized product photography."
        f"There should be no text nor people in the image."
    )
    
    return prompt


def generate_image(prompt, index, product_name, output_folder):
    # Clean meal name for filename
    clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-')).strip()
    clean_name = clean_name.replace(' ', '_')
    filename = f"{output_folder}/{index:03d}_{clean_name}.jpg"
    
    # Skip if image already exists
    if os.path.exists(filename):
        print(f"Image already exists for {product_name}, skipping...")
        return filename
        
    try:
        # Generate image using Stability AI API
        url = f"{STABILITY_API_HOST}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1.0
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Non-200 response: {response.text}")
            
        data = response.json()
        
        # Get image data from base64 string
        for i, image in enumerate(data["artifacts"]):
            image_data = BytesIO(base64.b64decode(image["base64"]))
            img = Image.open(image_data)
            
            # Resize to 384x384 - higher quality while still reasonable file size
            img = img.resize((384, 384), Image.Resampling.LANCZOS)
            
            # Save the image with higher quality compression
            img.save(filename, 'JPEG',
                    quality=70,  # Significantly increased quality
                    optimize=True)
            
            print(f"Successfully generated image for {product_name}")
            return filename  # Return the filename of the generated image
       
    except Exception as e:
        print(f"Error generating image for {product_name}: {str(e)}")
   
    # Sleep to respect rate limits
    sleep(1)
    return None


def find_all_meal_instances():
    """Find all instances of meals across all JSON files and their image locations"""
    # Dictionary to store meal name -> list of (json_file, index, product) tuples
    meal_instances = defaultdict(list)
    
    # List all JSON files in the current directory
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'meals' in data:
                    for index, product in enumerate(data['meals'], 1):
                        meal_name = product['name']
                        meal_instances[meal_name].append((json_file, index, product))
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    return meal_instances


def find_existing_images(meal_name, instances):
    """Find all existing images for a meal across all instances"""
    existing_images = []
    
    for json_file, index, product in instances:
        output_folder = f"images_{os.path.splitext(json_file)[0]}"
        clean_name = "".join(c for c in meal_name if c.isalnum() or c in (' ', '-')).strip()
        clean_name = clean_name.replace(' ', '_')
        image_path = f"{output_folder}/{index:03d}_{clean_name}.jpg"
        
        if os.path.exists(image_path):
            existing_images.append((image_path, json_file))
    
    return existing_images


def generate_new_image_for_meal(meal_name, instances):
    """Generate a new image for a meal using the first instance"""
    if not instances:
        return None
    
    # Use the first instance to generate a new image
    json_file, index, product = instances[0]
    output_folder = f"images_{os.path.splitext(json_file)[0]}_new"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    prompt = create_direct_prompt(product)
    print(f"Generating new image for {meal_name} using prompt: {prompt}")
    return generate_image(prompt, index, meal_name, output_folder)


def copy_image_to_all_instances(meal_name, instances, source_image_path):
    """Copy the selected image to all locations where this meal appears"""
    if not source_image_path or not os.path.exists(source_image_path):
        print(f"No source image found for {meal_name}")
        return
    
    # Copy the image to all instances
    for json_file, index, product in instances:
        output_folder = f"images_{os.path.splitext(json_file)[0]}"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        clean_name = "".join(c for c in meal_name if c.isalnum() or c in (' ', '-')).strip()
        clean_name = clean_name.replace(' ', '_')
        target_path = f"{output_folder}/{index:03d}_{clean_name}.jpg"
        
        # Copy the image
        try:
            shutil.copy2(source_image_path, target_path)
            print(f"Copied selected image to {target_path}")
        except Exception as e:
            print(f"Error copying image to {target_path}: {str(e)}")


class ImageSelectorApp:
    def __init__(self, root, meal_instances):
        self.root = root
        self.meal_instances = meal_instances
        self.meal_names = list(meal_instances.keys())
        self.current_meal_index = 0
        self.selected_image_path = None
        self.image_labels = []
        self.photo_references = []  # Keep references to prevent garbage collection
        
        # Configure the root window
        root.title("Meal Image Selector")
        root.geometry("1200x800")
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create meal navigation frame
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        # Previous meal button
        self.prev_button = ttk.Button(nav_frame, text="Previous Meal", command=self.prev_meal)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        # Meal name label
        self.meal_label = ttk.Label(nav_frame, text="", font=("Arial", 14, "bold"))
        self.meal_label.pack(side=tk.LEFT, padx=20)
        
        # Progress label
        self.progress_label = ttk.Label(nav_frame, text="")
        self.progress_label.pack(side=tk.LEFT, padx=20)
        
        # Next meal button
        self.next_button = ttk.Button(nav_frame, text="Next Meal", command=self.next_meal)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Create a frame with scrollbar for images
        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(scroll_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(scroll_frame, 
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars to scroll the canvas
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Create a frame inside the canvas to hold the images
        self.images_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.images_frame, anchor="nw")
        
        # Update scroll region when the size of the frame changes
        self.images_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Generate new image button
        self.generate_button = ttk.Button(main_frame, text="Generate New Image", command=self.generate_new_image)
        self.generate_button.pack(pady=10)
        
        # Apply selection button
        self.apply_button = ttk.Button(main_frame, text="Apply Selected Image to All Instances", command=self.apply_selection)
        self.apply_button.pack(pady=10)
        
        # Start with the first meal
        if self.meal_names:
            self.show_meal(0)
    
    def on_frame_configure(self, event):
        """Update the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """When the canvas changes size, update the window size"""
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def show_meal(self, index):
        """Display the meal at the given index"""
        if not self.meal_names:
            return
        
        # Clear previous images
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        self.image_labels = []
        self.photo_references = []
        self.selected_image_path = None
        
        # Get the current meal
        self.current_meal_index = index
        meal_name = self.meal_names[index]
        instances = self.meal_instances[meal_name]
        
        # Update labels
        self.meal_label.config(text=meal_name)
        self.progress_label.config(text=f"Meal {index + 1} of {len(self.meal_names)}")
        
        # Find existing images
        existing_images = find_existing_images(meal_name, instances)
        
        # Create a grid layout for images
        row = 0
        col = 0
        max_cols = 5  # Increased from 3 to 5 images per row
        
        # Display each image
        for i, (image_path, json_file) in enumerate(existing_images):
            try:
                # Create a frame for this image
                image_frame = ttk.Frame(self.images_frame)
                image_frame.grid(row=row, column=col, padx=5, pady=5)  # Reduced padding
                
                # Load and resize the image
                img = Image.open(image_path)
                img = img.resize((150, 150), Image.Resampling.LANCZOS)  # Reduced from 300x300 to 150x150
                photo = ImageTk.PhotoImage(img)
                self.photo_references.append(photo)  # Keep a reference
                
                # Create image label
                image_label = ttk.Label(image_frame, image=photo)
                image_label.pack()
                
                # Create source label with smaller font
                source_label = ttk.Label(image_frame, text=f"Source: {json_file}", font=("Arial", 8))
                source_label.pack()
                
                # Create select button with smaller size
                select_button = ttk.Button(
                    image_frame, 
                    text="Select", 
                    command=lambda path=image_path: self.select_image(path),
                    width=10  # Make button smaller
                )
                select_button.pack(pady=2)  # Reduced padding
                
                # Add to image labels
                self.image_labels.append((image_label, image_path))
                
                # Update grid position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
            except Exception as e:
                print(f"Error displaying image {image_path}: {str(e)}")
        
        # If no images found
        if not existing_images:
            no_images_label = ttk.Label(
                self.images_frame, 
                text="No existing images found for this meal. Click 'Generate New Image' to create one.",
                font=("Arial", 12)
            )
            no_images_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Update the scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def select_image(self, image_path):
        """Select an image as the best one"""
        self.selected_image_path = image_path
        
        # Highlight the selected image
        for label, path in self.image_labels:
            if path == image_path:
                label.configure(borderwidth=5, relief="solid")
            else:
                label.configure(borderwidth=0, relief="flat")
    
    def generate_new_image(self):
        """Generate a new image for the current meal"""
        if not self.meal_names:
            return
        
        meal_name = self.meal_names[self.current_meal_index]
        instances = self.meal_instances[meal_name]
        
        # Generate a new image
        new_image_path = generate_new_image_for_meal(meal_name, instances)
        
        if new_image_path:
            # Refresh the display to show the new image
            self.show_meal(self.current_meal_index)
        else:
            messagebox.showerror("Error", "Failed to generate a new image.")
    
    def apply_selection(self):
        """Apply the selected image to all instances of the current meal"""
        if not self.meal_names:
            return
        
        if not self.selected_image_path:
            messagebox.showwarning("No Selection", "Please select an image first.")
            return
        
        meal_name = self.meal_names[self.current_meal_index]
        instances = self.meal_instances[meal_name]
        
        # Copy the selected image to all instances
        copy_image_to_all_instances(meal_name, instances, self.selected_image_path)
        
        messagebox.showinfo("Success", f"Selected image has been applied to all instances of '{meal_name}'.")
        
        # Move to the next meal
        self.next_meal()
    
    def prev_meal(self):
        """Show the previous meal"""
        if not self.meal_names:
            return
        
        if self.current_meal_index > 0:
            self.show_meal(self.current_meal_index - 1)
    
    def next_meal(self):
        """Show the next meal"""
        if not self.meal_names:
            return
        
        if self.current_meal_index < len(self.meal_names) - 1:
            self.show_meal(self.current_meal_index + 1)
        else:
            messagebox.showinfo("Complete", "You've reached the last meal.")


def process_json_file(json_file):
    """Original function kept for backward compatibility"""
    # Get the base name without extension
    base_name = os.path.splitext(json_file)[0]
    
    # Create output directory name based on JSON filename
    output_folder = f"images_{base_name}"
    
    # Skip if this is the already processed maaltijdList
    if base_name == "maaltijdList":
        print(f"Skipping already processed {base_name}")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            meals = data['meals']
    except Exception as e:
        print(f"Error loading JSON file {json_file}: {str(e)}")
        return

    print(f"\nProcessing {json_file}...")
    for index, product in enumerate(meals, 1):
        print(f"\nProcessing product {index}/{len(meals)}: {product['name']}")
        prompt = create_direct_prompt(product)
        print(f"Using prompt: {prompt}")
        generate_image(prompt, index, product['name'], output_folder)
        print(f"Progress: {index}/{len(meals)}")


def list_meals_with_longest_names():
    """List the 10 meals with the longest names across all JSON files."""
    # Dictionary to store meal name -> length
    meal_name_lengths = {}
    # Dictionary to store meal name -> list of JSON files
    meal_json_files = defaultdict(list)
    
    # List all JSON files in the current directory
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    print("Scanning JSON files for meal names...")
    
    # Process each JSON file
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'meals' in data:
                    for meal in data['meals']:
                        meal_name = meal['name']
                        # Store the meal name and its length
                        meal_name_lengths[meal_name] = len(meal_name)
                        # Store which JSON file contains this meal
                        if json_file not in meal_json_files[meal_name]:
                            meal_json_files[meal_name].append(json_file)
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    # Sort meals by name length (descending) and take the top 10
    longest_meals = sorted(meal_name_lengths.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Print the results
    print("\n===== 10 Meals with Longest Names =====")
    for i, (meal_name, length) in enumerate(longest_meals, 1):
        json_list = ", ".join(meal_json_files[meal_name])
        # print(f"{i}. {meal_name} ({length} characters) - Found in: {json_list}")
        print(f"{i}. {meal_name} ({length} characters)")
    
    return longest_meals


def shorten_longest_meal_names():
    """
    Find the 10 meals with the longest names across all JSON files and replace them
    with shorter versions in all JSON files where they appear.
    """
    # Dictionary to store meal name -> length
    meal_name_lengths = {}
    # Dictionary to store meal name -> list of JSON files
    meal_json_files = defaultdict(list)
    
    # List all JSON files in the current directory
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    print("Scanning JSON files for meal names...")
    
    # Process each JSON file to find the longest meal names
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'meals' in data:
                    for meal in data['meals']:
                        meal_name = meal['name']
                        # Store the meal name and its length
                        meal_name_lengths[meal_name] = len(meal_name)
                        # Store which JSON file contains this meal
                        if json_file not in meal_json_files[meal_name]:
                            meal_json_files[meal_name].append(json_file)
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    # Sort meals by name length (descending) and take the top 10
    longest_meals = sorted(meal_name_lengths.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Create a mapping of old names to new names
    name_replacements = {
        longest_meals[0][0]: "chicken lettuce wraps",
        longest_meals[1][0]: "Tempeh Lettuce Wraps",
        longest_meals[2][0]: "Hummus Rice Cakes",
        longest_meals[3][0]: "Raspberry Bowl",
        longest_meals[4][0]: "Raspberry Shake",
        longest_meals[5][0]: "Berry Smoothie",
        longest_meals[6][0]: "Banana Pancakes",
        longest_meals[7][0]: "Berry Ice Cream",
        longest_meals[8][0]: "Lentils Pasta",
        longest_meals[9][0]: "Overnight Oats"
    }
    
    # Print the replacements that will be made
    print("\n===== Meal Name Replacements =====")
    for old_name, new_name in name_replacements.items():
        print(f"'{old_name}' -> '{new_name}'")
    
    # Now update each JSON file with the new names
    files_updated = 0
    meals_updated = 0
    
    for json_file in json_files:
        file_updated = False
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'meals' in data:
                for meal in data['meals']:
                    old_name = meal['name']
                    if old_name in name_replacements:
                        meal['name'] = name_replacements[old_name]
                        meals_updated += 1
                        file_updated = True
            
            if file_updated:
                # Write the updated data back to the file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files_updated += 1
                print(f"Updated meal names in: {json_file}")
                
        except Exception as e:
            print(f"Error updating {json_file}: {str(e)}")
    
    print(f"\nSummary: Updated {meals_updated} meal names across {files_updated} JSON files.")
    return longest_meals, name_replacements


def main():
    # List all JSON files in the current directory
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    # Uncomment the image generation part
    # First, generate images for all meals in all JSON files
    # print("Starting to generate images for all meals in all JSON files...")
    # for json_file in json_files:
    #     process_json_file(json_file)
    
    # print("Completed generating images for all meals")
    
    # Uncomment the image selection functionality
    # Find all meal instances across all JSON files
    meal_instances = find_all_meal_instances()
    print(f"Found {len(meal_instances)} unique meals across all JSON files")
    
    # # Create the Tkinter application
    root = tk.Tk()
    app = ImageSelectorApp(root, meal_instances)
    root.mainloop()


if __name__ == "__main__":
    # shorten_longest_meal_names()
    # list_meals_with_longest_names()
    main()

