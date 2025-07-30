"""
Simple Background Removal Module
A lightweight alternative that works reliably on Windows without DLL issues.
Uses cv2 and PIL for background removal with multiple algorithms.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io

class SimpleBackgroundRemover:
    """
    Lightweight background removal using OpenCV and PIL.
    Multiple algorithms for better results than U2Net.
    """
    
    def __init__(self):
        self.methods = ['grabcut', 'watershed', 'threshold']
    
    def remove_background_grabcut(self, image):
        """
        GrabCut algorithm for background removal.
        More accurate than simple thresholding.
        """
        try:
            # Convert PIL to OpenCV
            img_array = np.array(image.convert('RGB'))
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            height, width = img_cv.shape[:2]
            
            # Create mask
            mask = np.zeros((height, width), np.uint8)
            
            # Define rectangle around the main object (center 80% of image)
            margin_x = int(width * 0.1)
            margin_y = int(height * 0.1)
            rect = (margin_x, margin_y, width - 2*margin_x, height - 2*margin_y)
            
            # Initialize foreground and background models
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # Apply GrabCut
            cv2.grabCut(img_cv, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
            
            # Create final mask
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # Apply mask to image
            result = img_cv * mask2[:, :, np.newaxis]
            
            # Convert back to PIL with alpha
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            result_pil = Image.fromarray(result_rgb)
            
            # Create alpha channel from mask
            alpha = Image.fromarray((mask2 * 255).astype(np.uint8), 'L')
            result_pil.putalpha(alpha)
            
            return result_pil
            
        except Exception as e:
            print(f"GrabCut failed: {e}")
            return self._fallback_removal(image)
    
    def remove_background_watershed(self, image):
        """
        Watershed algorithm for background removal.
        Good for objects with clear boundaries.
        """
        try:
            # Convert to OpenCV
            img_array = np.array(image.convert('RGB'))
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Noise removal
            kernel = np.ones((3, 3), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
            
            # Sure background area
            sure_bg = cv2.dilate(opening, kernel, iterations=3)
            
            # Sure foreground area
            dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
            
            # Unknown region
            sure_fg = np.uint8(sure_fg)
            unknown = cv2.subtract(sure_bg, sure_fg)
            
            # Marker labelling
            _, markers = cv2.connectedComponents(sure_fg)
            markers = markers + 1
            markers[unknown == 255] = 0
            
            # Apply watershed
            markers = cv2.watershed(img_cv, markers)
            
            # Create mask
            mask = np.zeros(gray.shape, dtype=np.uint8)
            mask[markers > 1] = 255
            
            # Apply mask
            result = cv2.bitwise_and(img_cv, img_cv, mask=mask)
            
            # Convert back to PIL with alpha
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            result_pil = Image.fromarray(result_rgb)
            
            # Create alpha channel
            alpha = Image.fromarray(mask, 'L')
            result_pil.putalpha(alpha)
            
            return result_pil
            
        except Exception as e:
            print(f"Watershed failed: {e}")
            return self._fallback_removal(image)
    
    def remove_background_smart_threshold(self, image):
        """
        Smart thresholding with edge detection.
        Enhanced version of simple thresholding.
        """
        try:
            # Convert to OpenCV
            img_array = np.array(image.convert('RGB'))
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Convert to HSV for better color separation
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            # Create mask for background (assuming lighter background)
            # Adjust these values based on your typical images
            lower_bg = np.array([0, 0, 200])  # Light background
            upper_bg = np.array([180, 30, 255])
            
            bg_mask = cv2.inRange(hsv, lower_bg, upper_bg)
            
            # Invert mask to get foreground
            fg_mask = cv2.bitwise_not(bg_mask)
            
            # Apply morphological operations to clean up
            kernel = np.ones((5, 5), np.uint8)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Apply Gaussian blur for smoother edges
            fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
            
            # Apply mask
            result = cv2.bitwise_and(img_cv, img_cv, mask=fg_mask)
            
            # Convert back to PIL with alpha
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            result_pil = Image.fromarray(result_rgb)
            
            # Create alpha channel
            alpha = Image.fromarray(fg_mask, 'L')
            result_pil.putalpha(alpha)
            
            return result_pil
            
        except Exception as e:
            print(f"Smart threshold failed: {e}")
            return self._fallback_removal(image)
    
    def _fallback_removal(self, image):
        """
        Simple fallback method using PIL only.
        """
        try:
            # Convert to RGBA
            img = image.convert('RGBA')
            
            # Get image data
            data = img.getdata()
            
            # Create new data with transparency for white/light pixels
            new_data = []
            for item in data:
                # If pixel is mostly white/light, make it transparent
                if item[0] > 200 and item[1] > 200 and item[2] > 200:
                    new_data.append((255, 255, 255, 0))  # Transparent
                else:
                    new_data.append(item)
            
            # Update image data
            img.putdata(new_data)
            return img
            
        except Exception as e:
            print(f"Fallback removal failed: {e}")
            # Return original image with white background
            return image.convert('RGBA')
    
    def remove_background(self, image, method='auto'):
        """
        Remove background using specified method or auto-select best.
        
        Args:
            image (PIL.Image): Input image
            method (str): 'grabcut', 'watershed', 'threshold', or 'auto'
            
        Returns:
            PIL.Image: Image with background removed
        """
        if method == 'auto':
            # Try methods in order of quality
            for method_name in ['grabcut', 'watershed', 'threshold']:
                try:
                    if method_name == 'grabcut':
                        return self.remove_background_grabcut(image)
                    elif method_name == 'watershed':
                        return self.remove_background_watershed(image)
                    elif method_name == 'threshold':
                        return self.remove_background_smart_threshold(image)
                except Exception as e:
                    print(f"Method {method_name} failed: {e}")
                    continue
            
            # If all methods fail, use fallback
            return self._fallback_removal(image)
        
        elif method == 'grabcut':
            return self.remove_background_grabcut(image)
        elif method == 'watershed':
            return self.remove_background_watershed(image)
        elif method == 'threshold':
            return self.remove_background_smart_threshold(image)
        else:
            return self._fallback_removal(image)

# Global instance
_bg_remover = None

def get_simple_bg_remover():
    """Get or create global background remover instance."""
    global _bg_remover
    if _bg_remover is None:
        _bg_remover = SimpleBackgroundRemover()
    return _bg_remover

def remove_background_simple(image, method='auto'):
    """
    Simple background removal function.
    
    Args:
        image (PIL.Image): Input image
        method (str): Removal method
        
    Returns:
        PIL.Image: Image with background removed
    """
    remover = get_simple_bg_remover()
    return remover.remove_background(image, method)

# Compatibility function for existing code
def run_simple_bg_removal(pil_image):
    """
    Drop-in replacement for U2Net that works reliably.
    
    Args:
        pil_image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Mask image (L mode) for compatibility
    """
    try:
        # Remove background
        result = remove_background_simple(pil_image, method='auto')
        
        # Extract alpha channel as mask
        if result.mode == 'RGBA':
            mask = result.split()[-1]  # Alpha channel
        else:
            mask = result.convert('L')
        
        return mask
        
    except Exception as e:
        print(f"Simple background removal failed: {e}")
        # Return white mask as fallback
        return Image.new('L', pil_image.size, 255)
