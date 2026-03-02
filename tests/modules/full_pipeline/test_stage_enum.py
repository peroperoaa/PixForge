import pytest
from src.modules.full_pipeline.schemas import PipelineStage


class TestPipelineStageMembers:
    def test_has_exactly_four_members(self):
        """PipelineStage enum has exactly 4 members."""
        assert len(PipelineStage) == 4

    def test_members_in_order(self):
        """Members are PROMPT, IMAGE, PIXELIZATION, POST_PROCESSING."""
        members = list(PipelineStage)
        assert members[0] == PipelineStage.PROMPT
        assert members[1] == PipelineStage.IMAGE
        assert members[2] == PipelineStage.PIXELIZATION
        assert members[3] == PipelineStage.POST_PROCESSING


class TestPipelineStageOrdering:
    def test_prompt_less_than_image(self):
        assert PipelineStage.PROMPT < PipelineStage.IMAGE

    def test_image_less_than_pixelization(self):
        assert PipelineStage.IMAGE < PipelineStage.PIXELIZATION

    def test_pixelization_less_than_post_processing(self):
        assert PipelineStage.PIXELIZATION < PipelineStage.POST_PROCESSING

    def test_prompt_less_than_post_processing(self):
        assert PipelineStage.PROMPT < PipelineStage.POST_PROCESSING

    def test_equality(self):
        assert PipelineStage.PROMPT == PipelineStage.PROMPT
        assert PipelineStage.IMAGE == PipelineStage.IMAGE

    def test_greater_than(self):
        assert PipelineStage.POST_PROCESSING > PipelineStage.PROMPT

    def test_less_than_or_equal(self):
        assert PipelineStage.PROMPT <= PipelineStage.PROMPT
        assert PipelineStage.PROMPT <= PipelineStage.IMAGE

    def test_greater_than_or_equal(self):
        assert PipelineStage.IMAGE >= PipelineStage.IMAGE
        assert PipelineStage.IMAGE >= PipelineStage.PROMPT
