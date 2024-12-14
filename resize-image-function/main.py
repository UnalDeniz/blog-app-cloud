import os
from PIL import Image
from google.cloud import storage
from io import BytesIO

# Google Cloud Storage client
client = storage.Client()

def resize_image(data, context):
    """Cloud Function to resize the uploaded image and replace it in the same storage location"""
    
    # Bucket and file info
    bucket_name = data['bucket']
    file_name = data['name']
    
    # Size to which the image will be resized (change this to your required size)
    resized_width = 256  # Example width
    resized_height = 256  # Example height
    
    # Get the bucket and the blob (the file uploaded)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # Download the image
    image_data = blob.download_as_bytes()
    
    # Open the image with Pillow
    image = Image.open(BytesIO(image_data))

    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize the image
    image = image.resize((resized_width, resized_height))
    
    # Create a new BytesIO object to save the resized image into it
    with BytesIO() as output:
        image.save(output, format='JPEG')
        output.seek(0)  # Move the cursor to the start of the file
        
        # Upload the resized image back to the same location (overwriting the original)
        blob.upload_from_file(output, content_type='image/jpeg')
    
    print(f"Image {file_name} resized and replaced successfully.")
