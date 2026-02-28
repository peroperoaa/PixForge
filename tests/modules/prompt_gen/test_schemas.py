import pytest
from pydantic import ValidationError
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput

def test_prompt_input_valid():
    """Test valid PromptInput creation."""
    input_data = PromptInput(text_prompt="A majestic lion")
    assert input_data.text_prompt == "A majestic lion"
    assert input_data.image_path is None

    input_data_with_image = PromptInput(text_prompt="A majestic lion", image_path="/path/to/image.png")
    assert input_data_with_image.image_path == "/path/to/image.png"

def test_prompt_input_missing_required():
    """Test PromptInput missing required field."""
    with pytest.raises(ValidationError):
        PromptInput()

def test_prompt_input_invalid_type():
    """Test PromptInput invalid type."""
    # Strict validation requires explicit config, but default Pydantic coerces.
    # If we want strict types, we can check if it accepts an int as string or fails.
    # Usually standard Pydantic behavior is sufficient unless strict is required.
    # Here we test passing something that cannot be coerced easily or is clearly wrong type logic if we enforce strict.
    # Let's stick to standard behavior: passing a dict where string expected might fail?
    with pytest.raises(ValidationError):
        PromptInput(text_prompt={"not": "a string"})

def test_prompt_output_valid():
    """Test valid PromptOutput creation."""
    output_data = PromptOutput(
        positive_prompt="A beautiful sunset",
        negative_prompt="blurry, low quality",
        style_parameters={"style": "realistic"}
    )
    assert output_data.positive_prompt == "A beautiful sunset"
    assert output_data.negative_prompt == "blurry, low quality"
    assert output_data.style_parameters == {"style": "realistic"}

def test_prompt_output_missing_fields():
    """Test PromptOutput missing required fields."""
    with pytest.raises(ValidationError):
        PromptOutput(positive_prompt="Only positive")

def test_prompt_output_schema_export():
    """Test PromptOutput schema export."""
    schema = PromptOutput.model_json_schema()
    assert "properties" in schema
    assert "positive_prompt" in schema["properties"]
    assert "negative_prompt" in schema["properties"]
    assert "style_parameters" in schema["properties"]
