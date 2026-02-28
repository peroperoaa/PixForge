import os
import sys

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.config import ConfigManager
from src.modules.prompt_gen.schemas import PromptInput
from src.modules.prompt_gen.gemini_adapter import GeminiAdapter
from src.modules.prompt_gen.exceptions import APIConnectionError

def main():
    print("Initializing ConfigManager...")
    # This will load from .env by default via python-dotenv
    config = ConfigManager()
    
    try:
        api_key = config.get_api_key()
        print("API Key loaded successfully (redacted for security).")
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease create a .env file in the root directory containing:")
        print("API_KEY=your_actual_gemini_api_key_here")
        return
        
    print("\nInstantiating GeminiAdapter...")
    try:
        adapter = GeminiAdapter(config)
    except Exception as e:
        print(f"Failed to instantiate adapter: {e}")
        return
        
    print("\nPreparing input data...")
    input_data = PromptInput(text_prompt="test")
    
    print(f"Input text: '{input_data.text_prompt}'")
    
    print("\nGenerating prompt via Gemini API...")
    try:
        output_data = adapter.generate(input_data)
        
        print("\n--- Successful Verification ---")
        print("\nStructured PromptOutput result:")
        print(f"Positive Prompt:\n{output_data.positive_prompt}\n")
        print(f"Negative Prompt:\n{output_data.negative_prompt}\n")
        print("Style Parameters (if generated):")
        if output_data.style_parameters:
            for key, value in output_data.style_parameters.items():
                print(f"  {key}: {value}")
        else:
            print("  None")
            
    except APIConnectionError as e:
        print(f"\nAPI Error during verification: {e}")
        print("This could mean your API key is invalid or there is a network issue.")
    except Exception as e:
        print(f"\nUnexpected error during execution: {e}")

if __name__ == '__main__':
    main()