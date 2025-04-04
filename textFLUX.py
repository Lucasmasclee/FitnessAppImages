import os
import json
from time import sleep
import requests
from PIL import Image
from io import BytesIO


# Create output directory if it doesn't exist
if not os.path.exists('generated_images_products_flux'):
    os.makedirs('generated_images_products_flux')


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
        filename = f"generated_images_products_flux/{index:03d}_{clean_name}.jpg"
        image.save(filename, 'JPEG',
                  quality=70,  # Significantly increased quality
                  optimize=True)
           
        print(f"Successfully generated image for {product_name}")
       
    except Exception as e:
        print(f"Error generating image for {product_name}: {str(e)}")
   
    # Sleep to respect rate limits
    sleep(1)


# Load products from JSON file
try:
    with open('myProductList.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        products = data['productlist']  # Changed from 'meals' to 'productlist'
except Exception as e:
    print(f"Error loading JSON file: {str(e)}")
    exit(1)


# Process each product
for index, product in enumerate(products, 1):
    # Skip products before index 220
    if index < 0:
        continue
        
    print(f"\nProcessing product {index}/{len(products)}: {product['name']}")
    
    # Create prompt directly and generate image
    prompt = create_direct_prompt(product)
    print(f"Using prompt: {prompt}")
    generate_image_with_flux(prompt, index, product['name'])
    
    print(f"Progress: {index}/{len(products)}")