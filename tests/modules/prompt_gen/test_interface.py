import pytest
from src.modules.prompt_gen.interface import BasePromptGenerator
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput

def test_instantiate_abstract_class_raises_error():
    """Case 1: Instantiating BasePromptGenerator directly should raise TypeError."""
    with pytest.raises(TypeError) as exc_info:
        BasePromptGenerator()
    assert "Can't instantiate abstract class BasePromptGenerator" in str(exc_info.value)

def test_instantiate_incomplete_subclass_raises_error():
    """Case 2: Instantiating a subclass without generate method should raise TypeError."""
    class IncompleteGenerator(BasePromptGenerator):
        pass

    with pytest.raises(TypeError) as exc_info:
        IncompleteGenerator()
    assert "Can't instantiate abstract class IncompleteGenerator" in str(exc_info.value)

def test_instantiate_complete_subclass():
    """Case 3: Instantiating a subclass with generate method implemented should succeed."""
    class CompleteGenerator(BasePromptGenerator):
        def generate(self, input: PromptInput) -> PromptOutput:
            return PromptOutput(
                positive_prompt="A good prompt",
                negative_prompt="A bad prompt",
                style_parameters={"style": "raw"}
            )
            
    generator = CompleteGenerator()
    assert isinstance(generator, BasePromptGenerator)
    output = generator.generate(
        PromptInput(text_prompt="Test")
    )
    assert output.positive_prompt == "A good prompt"
