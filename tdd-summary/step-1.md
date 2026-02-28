# Step 1 - Understand Intent

## Functional Requirements

### FR-1: BasePromptGenerator Interface
- Create an abstract base class `BasePromptGenerator` in `src/modules/prompt_gen/interface.py`.
- It must accept `PromptInput` and return `PromptOutput` in an abstract method `generate(input: PromptInput) -> PromptOutput`.
- The class must prevent instantiation directly (being strictly abstract).
- Concrete subclasses must implement the `generate` method.

## Assumptions

- We will use `abc.ABC` and `abc.abstractmethod` to enforce the abstract constraint.
