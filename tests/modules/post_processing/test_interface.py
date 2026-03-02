import pytest
from src.modules.post_processing.interface import BasePostProcessor
from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


def test_base_post_processor_raises_type_error_on_direct_instantiation():
    """BasePostProcessor raises TypeError on direct instantiation."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePostProcessor()


def test_subclass_without_process_raises_type_error():
    """Subclass without process method raises TypeError on instantiation."""

    class IncompleteProcessor(BasePostProcessor):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteProcessor()


def test_concrete_subclass_can_be_instantiated():
    """Concrete subclass implementing process can be instantiated and called."""

    class ConcreteProcessor(BasePostProcessor):
        def process(self, input_data: PostProcessingInput) -> PostProcessingOutput:
            return PostProcessingOutput(
                output_paths=["/out/result.png"],
                target_sizes=input_data.target_sizes,
                color_count=input_data.color_count,
            )

    processor = ConcreteProcessor()
    assert isinstance(processor, BasePostProcessor)

    input_data = PostProcessingInput(
        image_path="input.png",
        asset_name="hero_sprite",
        target_sizes=[32, 64],
        color_count=16,
    )
    output = processor.process(input_data)
    assert output.output_paths == ["/out/result.png"]
    assert output.target_sizes == [32, 64]
    assert output.color_count == 16
