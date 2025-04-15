import os
import json
from time import sleep
import requests
from PIL import Image
from io import BytesIO


def create_direct_prompt(product):
    """Create a standardized prompt for consistent product photography"""
    name = product['name']
    
    prompt = (
        f"Ultra-realistic product photography of a single {name} on a pure white background. "
        f"The {name} should take up exactly 70% of the frame and be perfectly centered. "
        f"Shot directly from the front or top (whichever best shows the product), "
        f"with professional studio lighting. The {name} must be in its natural orientation "
        f"(not upside down). Style reference: stock photography for grocery stores. "
        f"Photorealistic, not artistic. The image must be clean, simple, and consistent "
        f"with standardized product photography."
        f"There should be no text nor people in the image."
    )
    
    return prompt


def generate_image_with_flux(prompt, index, product_name):
    try:
        # AIML API endpoint
        url = "https://api.aimlapi.com/v1/images/generations"  # Updated to AIML API endpoint
        
        # AIML API headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer a24a8167764f42989352430ecf869921"  # Your AIML API key
        }
        
        # AIML API payload (may need adjustments based on AIML API documentation)
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse the response
        response_data = response.json()
        
        # Get image URL and download (adjust based on actual AIML API response structure)
        # Note: You may need to adjust this path based on AIML API's actual response format
        image_url = response_data["data"][0]["url"]
        image_content = requests.get(image_url).content
       
        # Open the image with PIL
        image = Image.open(BytesIO(image_content))
       
        # Resize to 384x384 - higher quality while still reasonable file size
        image = image.resize((384, 384), Image.Resampling.LANCZOS)
       
        # Clean meal name for filename
        clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-')).strip()
        clean_name = clean_name.replace(' ', '_')
       
        # Save the image with higher quality compression
        filename = f"generated_images_products/{index:03d}_{clean_name}.jpg"
        image.save(filename, 'JPEG',
                  quality=70,  # Significantly increased quality
                  optimize=True)
           
        print(f"Successfully generated image for {product_name}")
       
    except Exception as e:
        print(f"Error generating image for {product_name}: {str(e)}")
   
    # Sleep to respect rate limits
    sleep(1)


def duplicate_existing_image(index, product_name):
    try:
        # Get list of existing images
        existing_images = os.listdir('generated_images_products')
        
        if not existing_images:
            print("No existing images found to duplicate")
            return False
        
        # Pick the first image to duplicate
        source_image_path = os.path.join('generated_images_products', existing_images[0])
        
        # Clean meal name for filename
        clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-')).strip()
        clean_name = clean_name.replace(' ', '_')
        
        # Create destination path
        dest_image_path = f"generated_images_products/{index:03d}_{clean_name}.jpg"
        
        # Open and save the image (creates a copy)
        image = Image.open(source_image_path)
        image.save(dest_image_path)
        
        print(f"Successfully duplicated image for {product_name}")
        return True
        
    except Exception as e:
        print(f"Error duplicating image for {product_name}: {str(e)}")
        return False


# Load products from JSON file
try:
    with open('myProductList.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        products = data['productlist']
except Exception as e:
    print(f"Error loading JSON file: {str(e)}")
    exit(1)

# Create output directory if it doesn't exist
if not os.path.exists('generated_images_products'):
    os.makedirs('generated_images_products')

# Process each product
for index, product in enumerate(products, 1):
    product_name = product['name']
    
    # Clean product name for filename
    clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-')).strip()
    clean_name = clean_name.replace(' ', '_')
    
    # Create the correct filename
    filename = f"generated_images_products/{index:03d}_{clean_name}.jpg"
    
    # Also check if image exists in the original folder
    original_folder_filename = f"generated_images_products/{index:03d}_{clean_name}.jpg"
    
    # Check if the file exists in either location
    if os.path.exists(filename):
        print(f"Image exists for {product_name}: {filename}")
    elif os.path.exists(original_folder_filename):
        # Copy from original folder to flux folder
        try:
            image = Image.open(original_folder_filename)
            image.save(filename)
            print(f"Copied image from original folder for {product_name}")
        except Exception as e:
            print(f"Error copying image from original folder: {str(e)}")
            duplicate_existing_image(index, product_name)
    else:
        print(f"Missing image for {product_name}, will duplicate an existing image")
        duplicate_existing_image(index, product_name)
    
    print(f"Progress: {index}/{len(products)}")