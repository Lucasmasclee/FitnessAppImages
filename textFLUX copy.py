import os

def rename_image_files(directory):
    """Rename image files to correct format based on product list"""
    try:
        # Get list of files in directory
        files = os.listdir(directory)
        
        # Filter for image files
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Process each file
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
                        os.rename(old_path, new_path)
                        print(f"Renamed: {file} → {new_filename}")
        
        print(f"Finished renaming files in {directory}")
        return True
    
    except Exception as e:
        print(f"Error renaming files in {directory}: {str(e)}")
        return False

def process_all_image_directories():
    """Process all image directories to rename files"""
    # Get all directories that start with 'images_'
    base_dirs = [d for d in os.listdir() if os.path.isdir(d) and d.startswith('images_')]
    
    for directory in base_dirs:
        print(f"Processing directory: {directory}")
        rename_image_files(directory)

# Main execution
if __name__ == "__main__":
    # Create output directory if it doesn't exist
    if not os.path.exists('generated_images_products'):
        os.makedirs('generated_images_products')
    
    # Process all image directories to rename files
    process_all_image_directories()
    
    print("Image renaming complete!")