import base64
import os

class VisionHandler:
    @staticmethod
    def encode_image_base64(image_path: str) -> str:
        """Reads a local image and encodes it to base64."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        # Determine mime type
        ext = image_path.split('.')[-1].lower()
        mime_type = "image/jpeg"
        if ext in ['png']: mime_type = "image/png"
        elif ext in ['webp']: mime_type = "image/webp"
        
        return f"data:{mime_type};base64,{encoded_string}"
        
    @staticmethod
    def construct_vision_message(text: str, image_url_or_path: str, is_local: bool = True) -> list:
        """Constructs the standard OpenAI format multimodal message array."""
        content = [{"type": "text", "text": text}]
        
        if is_local:
            base64_url = VisionHandler.encode_image_base64(image_url_or_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": base64_url
                }
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url_or_path
                }
            })
            
        return content
