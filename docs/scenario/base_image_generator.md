# Scenario: Base Image Generator Interface
- Given: An abstract base class `BaseImageGenerator` in `src/modules/image_gen` and its associated schemas `ImageGenInput`/`ImageGenOutput`.
- When: A developer attempts to instantiate it directly or subclasses it without implementing `generate`.
- Then: It should raise a `TypeError`.

- Given: A concrete subclass of `BaseImageGenerator`.
- When: It implements `generate` matching the signature.
- Then: It can be instantiated and the input/output schemas enforce typing.

## Test Steps

- Case 1 (Instantiation Blocked): Attempting to instantiate exactly `BaseImageGenerator` raises TypeError.
- Case 2 (Subclass Missing Implementation): Attempting to instantiate a subclass without `generate` raises TypeError.
- Case 3 (Concrete Class Success): A subclass that properly implements `generate` can be instantiated and behaves correctly.
- Case 4 (Schemas Typing): `ImageGenInput` and `ImageGenOutput` properly enforce defined fields.

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
