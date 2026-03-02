# Scenario: Subject-Aware Cropping
- Given: An image that may or may not have an alpha channel
- When: Subject-aware cropping is applied
- Then: If alpha exists, the bounding box of non-transparent pixels is used to center the subject in a square crop. If no alpha, center crop is used.

## Test Steps

- Case 1 (happy path): RGBA image with subject in top-left -> crop centers on subject's alpha bounding box
- Case 2 (center crop fallback): RGB image without alpha -> falls back to center crop
- Case 3 (crop_mode="center"): RGBA image with alpha but crop_mode="center" -> forces center crop
- Case 4 (full alpha coverage): RGBA image where entire image is opaque -> bounding box covers full image, equivalent to center crop
- Case 5 (small subject): RGBA image with tiny subject in corner -> crop is padded square around subject bounding box
- Case 6 (edge case): Image is already square -> crop returns image as-is for center crop

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
