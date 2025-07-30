"""
BiRefNet Background Removal Module
A simple and effective background removal implementation using BiRefNet model.
BiRefNet significantly outperforms U2Net in accuracy and edge quality.
"""

import os
from PIL import Image
import io
from rembg import remove, new_session

class BiRefNetBackgroundRemover:
    """
    Simple background removal using BiRefNet model.
    """
    
    def __init__(self, model_name='u2net'):
        """
        Initialize BiRefNet background remover.
        
        Args:
            model_name (str): Model to use (u2net for speed, birefnet-general for quality)
        """
        self.model_name = model_name
        self.session = None
        self._initialize_session()
    
    def _get_optimal_providers(self):
        """Get optimal ONNX Runtime providers for performance."""
        providers = []
        
        if self.enable_gpu:
            # Try GPU providers in order of preference
            available_providers = ort.get_available_providers()
            
            if 'CUDAExecutionProvider' in available_providers:
                providers.append(('CUDAExecutionProvider', {
                    'device_id': 0,
                    'arena_extend_strategy': 'kNextPowerOfTwo',
                    'gpu_mem_limit': 2 * 1024 * 1024 * 1024,  # 2GB limit
                    'cudnn_conv_algo_search': 'EXHAUSTIVE',
                    'do_copy_in_default_stream': True,
                }))
                print("🚀 CUDA GPU acceleration enabled")
            
            elif 'DmlExecutionProvider' in available_providers:
                providers.append('DmlExecutionProvider')
                print("🚀 DirectML GPU acceleration enabled")
        
        # Always add CPU as fallback
        if self.optimize_for_speed:
            providers.append(('CPUExecutionProvider', {
                'intra_op_num_threads': min(4, os.cpu_count()),
                'inter_op_num_threads': min(2, os.cpu_count()),
                'enable_cpu_mem_arena': True,
                'enable_memory_pattern': True,
            }))
        else:
            providers.append('CPUExecutionProvider')
        
        return providers
    
    def _initialize_session(self):
        """Initialize the rembg session with optimized BiRefNet model."""
        try:
            # For speed optimization, prefer faster models
            if self.optimize_for_speed and self.model_name == 'birefnet-general':
                # Try portrait model first (smaller, faster for most use cases)
                try:
                    self.session = new_session('birefnet-portrait')
                    self.model_name = 'birefnet-portrait'
                    print(f"✅ Optimized BiRefNet model '{self.model_name}' loaded for speed")
                    return
                except:
                    pass
            
            # Create session with requested model
            self.session = new_session(self.model_name)
            print(f"✅ BiRefNet model '{self.model_name}' loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Failed to load BiRefNet model '{self.model_name}': {e}")
            
            # Smart fallback strategy
            fallback_models = ['u2net', 'birefnet-general'] if self.optimize_for_speed else ['birefnet-general', 'u2net']
            
            for fallback_model in fallback_models:
                try:
                    self.session = new_session(fallback_model)
                    self.model_name = fallback_model
                    print(f"✅ Fallback to {fallback_model} model successful")
                    return
                except Exception as fallback_error:
                    print(f"⚠️ Failed to load {fallback_model}: {fallback_error}")
            
            raise Exception("Failed to load any background removal model")
    
    def _optimize_image_for_processing(self, input_image, max_size=1024):
        """Optimize image size for faster processing while maintaining quality."""
        if not self.optimize_for_speed:
            return input_image
        
        # Calculate optimal size
        width, height = input_image.size
        if max(width, height) > max_size:
            # Resize maintaining aspect ratio
            if width > height:
                new_width = max_size
                new_height = int((height * max_size) / width)
            else:
                new_height = max_size
                new_width = int((width * max_size) / height)
            
            # Use high-quality resampling
            optimized = input_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return optimized, (width, height)  # Return original size for later restoration
        
        return input_image, None
    
    def remove_background(self, input_image):
        """
        Remove background from image using optimized BiRefNet.
        
        Args:
            input_image (PIL.Image): Input image
            
        Returns:
            PIL.Image: Image with background removed (RGBA format)
        """
        start_time = time.time()
        
        try:
            # Optimize image size for speed
            processed_image, original_size = self._optimize_image_for_processing(input_image)
            
            # Convert PIL Image to bytes with optimal format
            img_byte_arr = io.BytesIO()
            # Use JPEG for faster processing if no transparency needed
            if processed_image.mode in ('RGBA', 'LA'):
                processed_image.save(img_byte_arr, format='PNG', optimize=True)
            else:
                processed_image.save(img_byte_arr, format='JPEG', quality=95, optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remove background using BiRefNet
            output_bytes = remove(img_byte_arr, session=self.session)
            
            # Convert back to PIL Image
            output_image = Image.open(io.BytesIO(output_bytes))
            
            # Restore original size if it was resized
            if original_size:
                output_image = output_image.resize(original_size, Image.Resampling.LANCZOS)
            
            # Ensure RGBA format
            if output_image.mode != 'RGBA':
                output_image = output_image.convert('RGBA')
            
            # Track performance
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 10:
                self.processing_times.pop(0)
            
            avg_time = sum(self.processing_times) / len(self.processing_times)
            print(f"⚡ Background removal completed in {processing_time:.2f}s (avg: {avg_time:.2f}s)")
            
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

# Global instances for efficient reuse
_bg_remover = None
_fast_bg_remover = None

def get_bg_remover(model_name='birefnet-general', fast_mode=False):
    """Get or create global BiRefNet background remover instance."""
    global _bg_remover, _fast_bg_remover
    
    if fast_mode:
        if _fast_bg_remover is None:
            # Create optimized instance for speed
            _fast_bg_remover = BiRefNetBackgroundRemover(
                model_name='u2net',  # Fastest model
                enable_gpu=True,
                optimize_for_speed=True
            )
        return _fast_bg_remover
    else:
        if _bg_remover is None or _bg_remover.model_name != model_name:
            _bg_remover = BiRefNetBackgroundRemover(
                model_name=model_name,
                enable_gpu=True,
                optimize_for_speed=True
            )
        return _bg_remover

def remove_background_birefnet(input_image, model_name='birefnet-general', advanced=True, fast_mode=False):
    """
    Convenient function to remove background using BiRefNet with speed options.
    
    Args:
        input_image (PIL.Image): Input image
        model_name (str): BiRefNet model to use
        advanced (bool): Use advanced mode with alpha matting
        fast_mode (bool): Use fastest possible processing (may reduce quality)
        
    Returns:
        PIL.Image: Image with background removed
    """
    if fast_mode:
        # Use fastest processing
        remover = get_bg_remover(model_name='u2net', fast_mode=True)
        return remover.remove_background(input_image)
    else:
        remover = get_bg_remover(model_name)
        
        if advanced:
            return remover.remove_background_advanced(input_image)
        else:
            return remover.remove_background(input_image)

def remove_background_fast(input_image):
    """
    Ultra-fast background removal with optimized settings.
    
    Args:
        input_image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Image with background removed
    """
    return remove_background_birefnet(input_image, fast_mode=True)

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
