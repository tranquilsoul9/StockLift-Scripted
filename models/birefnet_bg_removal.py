"""
BiRefNet Background Removal Module
A powerful background removal implementation using BiRefNet model via rembg library.
BiRefNet significantly outperforms U2Net in accuracy and edge quality.
"""

import os
import numpy as np
from PIL import Image
import io
from rembg import remove, new_session

class BiRefNetBackgroundRemover:
    """
    High-performance background removal using BiRefNet model.
    BiRefNet is state-of-the-art for dichotomous image segmentation.
    """
    
    def __init__(self, model_name='birefnet-general'):
        """
        Initialize BiRefNet background remover.
        
        Args:
            model_name (str): Model to use. Options:
                - 'birefnet-general': Best overall performance
                - 'birefnet-portrait': Optimized for people
                - 'birefnet-massive': Trained on massive dataset
        """
        self.model_name = model_name
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize the rembg session with BiRefNet model."""
        try:
            # Create session with BiRefNet model
            self.session = new_session(self.model_name)
            print(f"✅ BiRefNet model '{self.model_name}' loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load BiRefNet model '{self.model_name}': {e}")
            # Fallback to general model
            try:
                self.session = new_session('birefnet-general')
                print("✅ Fallback to birefnet-general model successful")
            except Exception as fallback_error:
                print(f"❌ Failed to load any BiRefNet model: {fallback_error}")
                # Final fallback to u2net
                self.session = new_session('u2net')
                print("⚠️ Using U2Net as final fallback")
    
    def remove_background(self, input_image):
        """
        Remove background from image using BiRefNet.
        
        Args:
            input_image (PIL.Image): Input image
            
        Returns:
            PIL.Image: Image with background removed (RGBA format)
        """
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            input_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remove background using BiRefNet
            output_bytes = remove(img_byte_arr, session=self.session)
            
            # Convert back to PIL Image
            output_image = Image.open(io.BytesIO(output_bytes))
            
            # Ensure RGBA format
            if output_image.mode != 'RGBA':
                output_image = output_image.convert('RGBA')
            
            return output_image
            
        except Exception as e:
            print(f"❌ BiRefNet background removal failed: {e}")
            # Return original image with white background as fallback
            fallback = Image.new('RGBA', input_image.size, (255, 255, 255, 255))
            fallback.paste(input_image, (0, 0))
            return fallback
    
    def remove_background_advanced(self, input_image, alpha_matting=True, alpha_matting_foreground_threshold=270, alpha_matting_background_threshold=10):
        """
        Advanced background removal with alpha matting for better edge quality.
        
        Args:
            input_image (PIL.Image): Input image
            alpha_matting (bool): Enable alpha matting for smoother edges
            alpha_matting_foreground_threshold (int): Foreground threshold (0-255)
            alpha_matting_background_threshold (int): Background threshold (0-255)
            
        Returns:
            PIL.Image: Image with background removed (RGBA format)
        """
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            input_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remove background with advanced options
            if alpha_matting:
                output_bytes = remove(
                    img_byte_arr, 
                    session=self.session,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                    alpha_matting_erode_size=10
                )
            else:
                output_bytes = remove(img_byte_arr, session=self.session)
            
            # Convert back to PIL Image
            output_image = Image.open(io.BytesIO(output_bytes))
            
            # Ensure RGBA format
            if output_image.mode != 'RGBA':
                output_image = output_image.convert('RGBA')
            
            return output_image
            
        except Exception as e:
            print(f"❌ Advanced BiRefNet background removal failed: {e}")
            # Fallback to basic removal
            return self.remove_background(input_image)

# Global instance for efficient reuse
_bg_remover = None

def get_bg_remover(model_name='birefnet-general'):
    """Get or create global BiRefNet background remover instance."""
    global _bg_remover
    if _bg_remover is None or _bg_remover.model_name != model_name:
        _bg_remover = BiRefNetBackgroundRemover(model_name)
    return _bg_remover

def remove_background_birefnet(input_image, model_name='birefnet-general', advanced=True):
    """
    Convenient function to remove background using BiRefNet.
    
    Args:
        input_image (PIL.Image): Input image
        model_name (str): BiRefNet model to use
        advanced (bool): Use advanced mode with alpha matting
        
    Returns:
        PIL.Image: Image with background removed
    """
    remover = get_bg_remover(model_name)
    
    if advanced:
        return remover.remove_background_advanced(input_image)
    else:
        return remover.remove_background(input_image)

# Compatibility function to replace U2Net
def run_birefnet(pil_image):
    """
    Drop-in replacement for run_u2net function.
    
    Args:
        pil_image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Mask image (L mode) for compatibility
    """
    try:
        # Remove background using BiRefNet
        result = remove_background_birefnet(pil_image, advanced=True)
        
        # Extract alpha channel as mask for compatibility with existing code
        if result.mode == 'RGBA':
            # Get alpha channel
            mask = result.split()[-1]  # Alpha channel
        else:
            # Convert to grayscale if no alpha
            mask = result.convert('L')
        
        return mask
        
    except Exception as e:
        print(f"❌ BiRefNet processing failed: {e}")
        # Return white mask as fallback
        return Image.new('L', pil_image.size, 255)
