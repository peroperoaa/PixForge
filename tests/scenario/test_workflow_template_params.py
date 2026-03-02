"""Tests for workflow template parameter values (FR-1)."""
import json
import pytest


@pytest.fixture
def workflow_template():
    """Load the actual workflow_api_template.json."""
    with open("workflow_api_template.json", "r", encoding="utf-8") as f:
        return json.load(f)


class TestWorkflowTemplateParams:
    """Verify that workflow_api_template.json has optimised parameter values."""

    def test_ksampler_denoise_is_032(self, workflow_template):
        """KSampler denoise must be 0.32 for low-res pixel art."""
        assert workflow_template["3"]["inputs"]["denoise"] == 0.32

    def test_controlnet_strength_is_065(self, workflow_template):
        """ControlNetApply strength must be 0.65."""
        assert workflow_template["10"]["inputs"]["strength"] == 0.65

    def test_negative_prompt_includes_anatomy_terms(self, workflow_template):
        """Negative prompt must include anatomy-preserving exclusion terms."""
        neg_text = workflow_template["5"]["inputs"]["text"]
        for term in ["deformed", "bad anatomy", "extra limbs", "mutation"]:
            assert term in neg_text, f"'{term}' missing from negative prompt"

    def test_positive_prompt_is_placeholder(self, workflow_template):
        """Positive prompt should be a generic placeholder, not a specific prompt."""
        pos_text = workflow_template["2"]["inputs"]["text"]
        assert pos_text == "{prompt}", \
            f"Positive prompt should be '{{prompt}}' placeholder, got: {pos_text}"
