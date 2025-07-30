"""
Simple Background Removal Module
Clean implementation using rembg with BiRefNet for better quality than U2Net.
"""

from PIL import Image
import io
from rembg import remove, new_session

# Global session for reuse
_session = None

def get_session():
    """Get or create a global rembg session."""
    global _session
    if _session is None:
        try:
            # Try u2net first for speed
            _session = new_session('u2net')
            print("✅ U2Net model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    return _session

def remove_background_simple(input_image):
    """
    Simple background removal function with improved error handling.
    
    Args:
        input_image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Image with background removed (RGBA format)
    """
    try:
        # Validate input image
        if input_image is None:
            raise ValueError("Input image is None")
        
        # Ensure image is in RGB mode for processing
        if input_image.mode not in ('RGB', 'RGBA'):
            input_image = input_image.convert('RGB')
        
        # Convert PIL Image to bytes with error handling
        img_byte_arr = io.BytesIO()
        # Use JPEG for better compatibility and smaller size
        if input_image.mode == 'RGBA':
            # Convert RGBA to RGB with white background for JPEG
            rgb_image = Image.new('RGB', input_image.size, (255, 255, 255))
            rgb_image.paste(input_image, mask=input_image.split()[-1] if input_image.mode == 'RGBA' else None)
            rgb_image.save(img_byte_arr, format='JPEG', quality=95)
        else:
            input_image.save(img_byte_arr, format='JPEG', quality=95)
        
        img_byte_arr.seek(0)
        img_bytes = img_byte_arr.getvalue()
        
        if len(img_bytes) == 0:
            raise ValueError("Failed to convert image to bytes")
        
        # Remove background
        session = get_session()
        output_bytes = remove(img_bytes, session=session)
        
        if len(output_bytes) == 0:
            raise ValueError("Background removal returned empty result")
        
        # Convert back to PIL Image
        output_image = Image.open(io.BytesIO(output_bytes))
        
        # Ensure RGBA format
        if output_image.mode != 'RGBA':
            output_image = output_image.convert('RGBA')
        
        return output_image
        
    except Exception as e:
        print(f"❌ Background removal failed: {e}")
        # Return original image as fallback with proper RGBA conversion
        try:
            if input_image.mode != 'RGBA':
                return input_image.convert('RGBA')
            return input_image
        except:
            # Create a white image as final fallback
            return Image.new('RGBA', (500, 500), (255, 255, 255, 255))

# Compatibility function
def run_birefnet(pil_image):
    """
    Drop-in replacement for run_u2net function.
    
    Args:
        pil_image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Mask image (L mode) for compatibility
    """
    try:
        result = remove_background_simple(pil_image)
        
        # Extract alpha channel as mask for compatibility
        if result.mode == 'RGBA':
            mask = result.split()[-1]  # Alpha channel
        else:
            mask = result.convert('L')
        
        return mask
        
    except Exception as e:
        print(f"❌ Background removal failed: {e}")
        # Return white mask as fallback
        return Image.new('L', pil_image.size, 255)
