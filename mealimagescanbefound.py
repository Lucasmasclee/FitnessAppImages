import os
import json
import requests
from urllib.parse import quote

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def main():
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the Resources directory
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Server base URL from Voeding.cs
    server_base_url = "https://fitnessappimages.onrender.com/"
    
    # Find all JSON files in the directory that might contain meal lists
    json_files = [f for f in os.listdir() if f.endswith('.json') and 'maaltijd' in f.lower()]
    
    print(f"Found {len(json_files)} meal list JSON files")
    for f in json_files:
        print(f"  - {f}")
    
    if not json_files:
        print("No meal list JSON files found in the current directory.")
        return
    
    # Dictionary to store results
    missing_images = []
    
    # Process each JSON file
    for json_file in json_files:
        file_path = os.path.join(os.getcwd(), json_file)
        meal_data = load_json_file(file_path)
        
        if not meal_data or 'meals' not in meal_data:
            print(f"Skipping {json_file}: No meals found")
            continue
        
        # Get folder name for this meal list (without .json extension)
        folder_name = "images_" + json_file.replace('.json', '')
        
        print(f"\nChecking images for {json_file} in folder {folder_name}...")
        
        # Check each meal's image
        for i, meal in enumerate(meal_data['meals']):
            # Generate image filename as in Voeding.cs
            product_index = i + 1
            image_name = f"{product_index:03d}_{meal['name'].replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')}.jpg"
            
            # Create the full URL
            image_url = server_base_url + quote(folder_name) + "/" + quote(image_name)
            
            # Check if the image exists - try both original case and lowercase
            found = False
            urls_to_try = [
                image_url,  # Original case
                server_base_url + quote(folder_name) + "/" + quote(image_name.lower())  # Lowercase version
            ]
            
            for url in urls_to_try:
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        found = True
                        break
                except Exception:
                    pass
            
            if found:
                # Image found, do nothing
                pass
            else:
                print(f"✗ Missing: {image_name}")
                missing_images.append({
                    "file": json_file,
                    "meal": meal['name'],
                    "url": image_url
                })
    
    # Print summary
    print("\n--- MISSING IMAGES ---")
    if missing_images:
        print(f"Total images missing: {len(missing_images)}")
        print("\nList of meals with missing images:")
        for item in missing_images:
            print(f"- {item['meal']} (from {item['file']})")
    else:
        print("All meal images were found!")
    
    # Save results to a JSON file
    results_file = os.path.join(os.getcwd(), "missing_meal_images.json")
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(missing_images, f, indent=2)
        print(f"\nDetailed results saved to {results_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()