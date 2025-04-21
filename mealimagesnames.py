import os
import json
import shutil

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

def rename_image_files(directory):
    """Rename image files to correct format based on product list and replace content with first image"""
    try:
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
        
        # Create placeholder files for missing images
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

# Main execution
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists('generated_images_products'):
        os.makedirs('generated_images_products')
    
    # Process all image directories to rename files and create missing ones
    process_all_image_directories()
    
    print("Image processing complete!")