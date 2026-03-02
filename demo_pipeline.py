import os
import sys

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.config import ConfigManager
from src.modules.image_generation_pipeline import ImageGenerationPipeline

def main():
    print("Initializing ConfigManager...")
    config = ConfigManager()
    
    try:
        api_key = config.get_api_key()
        print("API Key loaded successfully (redacted for security).")
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease create a .env file in the root directory containing:")
        print("API_KEY=your_actual_gemini_api_key_here")
        return

    # Initialize Pipeline
    print("\nInstantiating ImageGenerationPipeline...")
    try:
        pipeline = ImageGenerationPipeline(config)
    except Exception as e:
        print(f"Failed to instantiate pipeline: {e}")
        return

    # Step 1: User Input
    user_prompt = "A futuristic city with flying cars"
    print(f"\nUser Input: '{user_prompt}'")

    # Step 2: Generate Image
    print("\n--- Pipeline: Generating Image ---")
    
    image_path = pipeline.generate_image(user_prompt)
    
    if image_path:
        print(f"\nImage Generated Successfully!")
        print(f"Image Path: {image_path}")
        
        if os.path.exists(image_path):
            size_kb = os.path.getsize(image_path) / 1024
            print(f"File Output Verified. Size: {size_kb:.2f} KB")
    else:
        print("Image Generation Failed.")

if __name__ == "__main__":
    main()
