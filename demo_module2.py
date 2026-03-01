import os
import sys

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.config import ConfigManager
from src.modules.image_gen.schemas import ImageGenInput
from src.modules.image_gen.gemini_adapter import GeminiImageAdapter

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
        
    print("\nInstantiating GeminiImageAdapter...")
    try:
        adapter = GeminiImageAdapter(config)
    except Exception as e:
        print(f"Failed to instantiate adapter: {e}")
        return
        
    print("\nPreparing dummy prompt from Module 1...")
    # Using a dummy prompt that would typically come from Module 1 (Prompt Gen)
    dummy_positive_prompt = "A high-quality, photorealistic image of a futuristic city skyline at sunset, with flying cars and neon lights, cinematic lighting, 8k resolution."
    input_data = ImageGenInput(prompt=dummy_positive_prompt)
    
    print(f"Input Prompt: '{input_data.prompt}'")
    
    print(f"\nGenerating image via Gemini API (Model: {adapter.model_name})...")
    print("This might take a few seconds...")
    try:
        output_data = adapter.generate(input_data)
        
        print("\n--- Successful Verification ---")
        print(f"Image downloaded and saved successfully!")
        print(f"Image Path: {output_data.image_path}")
        
        # Verify the file actually exists
        if os.path.exists(output_data.image_path):
            size_kb = os.path.getsize(output_data.image_path) / 1024
            print(f"File Output Verified. Size: {size_kb:.2f} KB")
        else:
            print(f"Warning: File path was returned but file does not exist at {output_data.image_path}")
            
    except Exception as e:
        print("\n--- Generation Failed ---")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
