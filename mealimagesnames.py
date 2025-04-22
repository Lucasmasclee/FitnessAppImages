import os
import json
import shutil
from collections import defaultdict

def get_missing_files_by_directory():
    """Return a dictionary of missing files for each directory"""
    missing_files = {
        'images_maaltijdList - Dairy&GLuten-Free': [
            '011_Chicken_Wrap.jpg',
            '019_Pizza.jpg',
            '022_Strawberry_Shake.jpg',
            '023_Peanut_Butter_Shake.jpg'
        ],
        'images_maaltijdList - Dairy-Free': [
            '006_Chicken_Salad.jpg',
            '022_Strawberry_Shake.jpg',
            '023_Peanut_Butter_Shake.jpg'
        ],
        'images_maaltijdList - Gluten-Free': [
            '006_Chicken_Salad.jpg',
            '019_Pizza_Rounds.jpg',
            '022_Strawberry_Shake.jpg',
            '023_Peanut_Butter_Shake.jpg'
        ],
        'images_maaltijdList - Vegan&Gluten-Free': [
            '002_Almond_Banana_Pancakes.jpg',
            '006_Spicy_Tofu_Salad.jpg',
            '007_Edamame_Rice_Cakes.jpg',
            '010_Tomato_Lentils_Pasta.jpg',
            '011_Tempeh_Lettuce_Wraps_with_Rice_Cakes.jpg',
            '015_Cottage_Cheese_Bowl.jpg',
            '016_Hummus_Rice_Cakes.jpg',
            '018_Tofu_Poke_Bowl.jpg',
            '019_Pizza_Rounds.jpg',
            '022_Raspberry_Smoothie_Bowl.jpg',
            '023_Raspberry_Protein_Shake.jpg'
        ],
        'images_maaltijdList - Vegan': [
            '010_Tomato_Lentils_Pasta.jpg',
            '016_Hummus_Rice_Cakes.jpg',
            '019_Pizza_Rounds.jpg',
            '022_Raspberry_Smoothie_Bowl.jpg',
            '023_Raspberry_Protein_Shake.jpg'
        ],
        'images_maaltijdList - Vegetar,Dairy,Gluten': [
            '016_Cheese-Hummus_Rice_Cakes.jpg',
            '019_Potato_Pizza_Rounds.jpg',
            '020_Tempeh_Rice_Bowl.jpg',
            '022_Raspberry_Smoothie_Bowl.jpg',
            '023_Raspberry_Protein_Shake.jpg'
        ],
        'images_maaltijdList - Vegetarian&Dairy-Free': [
            '016_Cheese-Hummus_Rice_Cakes.jpg',
            '019_Potato_Pizza_Rounds.jpg',
            '020_Tempeh_Rice_Bowl.jpg',
            '022_Raspberry_Smoothie_Bowl.jpg',
            '023_Raspberry_Protein_Shake.jpg'
        ],
        'images_maaltijdList - Vegetarian&Gluten-Free': [
            '016_Cheese-Hummus_Rice_Cakes.jpg',
            '019_Potato_Pizza_Rounds.jpg',
            '020_Tempeh_Rice_Bowl.jpg',
            '022_Raspberry_Smoothie_Bowl.jpg',
            '023_Raspberry_Protein_Shake.jpg'
        ],
        'images_maaltijdList - Vegetarian': [
            '016_Cheese-Hummus_Rice_Cakes.jpg',
            '019_Potato_Pizza_Rounds.jpg',
            '020_Tempeh_Rice_Bowl.jpg',
            '022_Raspberry_Smoothie_Bowl.jpg',
            '023_Raspberry_Protein_Shake.jpg'
        ],
        'images_maaltijdList': [
            '022_Strawberry_Shake.jpg',
            '023_Peanut_Butter_Shake.jpg'
        ]
    }
    return missing_files

def get_meal_name_mappings():
    """Get mappings between original meal names and shortened versions"""
    # Original to shortened meal name mappings
    name_mappings = {
        "Chicken Lettuce Wraps with Rice Cakes": "chicken lettuce wraps",
        "Tempeh Lettuce Wraps with Rice Cakes": "Tempeh Lettuce Wraps",
        "Cheese-Hummus Rice Cakes": "Hummus Rice Cakes",
        "Raspberry Smoothie Bowl": "Raspberry Bowl",
        "Raspberry Protein Shake": "Raspberry Shake",
        "Berry Protein Smoothie": "Berry Smoothie",
        "Almond Banana Pancakes": "Banana Pancakes",
        "Strawberry Ice Cream": "Berry Ice Cream",
        "Tomato Lentils Pasta": "Lentils Pasta",
        "Overnight Oats Bowl": "Overnight Oats"
    }
    
    # Create reverse mapping for filename matching
    filename_mappings = {}
    for old_name, new_name in name_mappings.items():
        # Convert to filename format (replace spaces with underscores)
        old_filename = old_name.replace(' ', '_')
        new_filename = new_name.replace(' ', '_')
        filename_mappings[old_filename] = new_filename
    
    return name_mappings, filename_mappings

def rename_image_files(directory):
    """Rename image files to correct format based on product list and replace content with first image"""
    try:
        # Get name mappings
        _, filename_mappings = get_meal_name_mappings()
        
        # Get list of files in directory
        files = os.listdir(directory)
        
        # Filter for image files
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Find the first image to use as a replacement
        first_image = None
        for file in sorted(image_files):
            if len(file) >= 3 and file[:3].isdigit():
                first_image = os.path.join(directory, file)
                break
        
        if not first_image:
            print(f"No valid image found in {directory} to use as replacement")
            return False
        
        # Process each file
        renamed_files = []
        for file in image_files:
            # Extract the index part (first 3 characters)
            if len(file) >= 3 and file[:3].isdigit():
                index = file[:3]
                
                # Get the rest of the filename after the index and underscore
                if '_' in file[3:]:
                    name_part = file[file.index('_')+1:]
                    
                    # Check if this name needs to be updated based on our mappings
                    name_without_ext, ext = os.path.splitext(name_part)
                    
                    # Try to find a match in our mappings
                    matched = False
                    for old_name, new_name in filename_mappings.items():
                        if old_name.lower() in name_without_ext.lower():
                            # Create new filename with the shortened name
                            clean_name = new_name + ext
                            new_filename = f"{index}_{clean_name}"
                            matched = True
                            break
                    
                    # If no match found, just clean the existing name
                    if not matched:
                        # Clean the name part
                        clean_name = "".join(c for c in name_part if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                        # Create new filename
                        new_filename = f"{index}_{clean_name}"
                    
                    # Rename only if the filename would change
                    if file != new_filename:
                        old_path = os.path.join(directory, file)
                        new_path = os.path.join(directory, new_filename)
                        
                        # First rename the file
                        os.rename(old_path, new_path)
                        print(f"Renamed: {file} → {new_filename}")
                        
                        # Add to list of renamed files
                        renamed_files.append(new_path)
        
        # Replace content of renamed files with first image
        for renamed_file in renamed_files:
            try:
                # Copy the content of the first image to the renamed file
                shutil.copy2(first_image, renamed_file)
                print(f"Replaced content of {os.path.basename(renamed_file)} with content from {os.path.basename(first_image)}")
            except Exception as e:
                print(f"Error replacing content of {os.path.basename(renamed_file)}: {str(e)}")
        
        print(f"Finished renaming files in {directory}")
        return True
    
    except Exception as e:
        print(f"Error renaming files in {directory}: {str(e)}")
        return False

def create_missing_files(directory, missing_files):
    """Create placeholder files for missing images and remove incorrect ones"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        
        # Get list of existing image files
        existing_files = []
        if os.path.exists(directory):
            existing_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Find the first image to use as a template
        template_image = None
        for file in sorted(existing_files):
            if len(file) >= 3 and file[:3].isdigit():
                template_image = os.path.join(directory, file)
                break
        
        # Extract indices of missing files
        missing_indices = [file[:3] for file in missing_files]
        
        # Remove existing files with the same indices as missing files
        for file in existing_files:
            if len(file) >= 3 and file[:3].isdigit() and file[:3] in missing_indices:
                # This is an incorrect file with the same index as a missing file
                file_path = os.path.join(directory, file)
                os.remove(file_path)
                print(f"Removed incorrect file: {file} from {directory}")
        
        # Create placeholder files for missing images - commented out for now
        """
        for filename in missing_files:
            file_path = os.path.join(directory, filename)
            if not os.path.exists(file_path):
                if template_image and os.path.exists(template_image):
                    # Copy the template image to create the missing file
                    shutil.copy2(template_image, file_path)
                    print(f"Created placeholder for: {filename} in {directory} using template image")
                else:
                    # Create an empty file as a placeholder if no template is available
                    with open(file_path, 'w') as f:
                        f.write("Placeholder for missing image")
                    print(f"Created placeholder for: {filename} in {directory} (text placeholder)")
        """
        
        return True
    except Exception as e:
        print(f"Error processing files in {directory}: {str(e)}")
        return False

def process_all_image_directories():
    """Process all image directories to rename files and create missing ones"""
    # Get the dictionary of missing files by directory
    missing_files_dict = get_missing_files_by_directory()
    
    # Get all directories that start with 'images_'
    base_dirs = [d for d in os.listdir() if os.path.isdir(d) and d.startswith('images_')]
    
    # Process existing directories
    for directory in base_dirs:
        print(f"Processing directory: {directory}")
        rename_image_files(directory)
        
        # Create missing files if this directory is in our list
        if directory in missing_files_dict:
            create_missing_files(directory, missing_files_dict[directory])
    
    # Create any missing directories from our list
    for directory in missing_files_dict:
        if directory not in base_dirs and missing_files_dict[directory]:
            print(f"Creating missing directory: {directory}")
            create_missing_files(directory, missing_files_dict[directory])

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

# Main execution
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists('generated_images_products'):
        os.makedirs('generated_images_products')
    
    # Process all image directories to rename files and create missing ones
    process_all_image_directories()
    
    print("Image processing complete!")