# Scenario: Artifact Detector - Scan Output Directory
- Given: An output directory that may contain `images/` and `assets/` subdirectories with various files
- When: ArtifactDetector scans the directory
- Then: Files are correctly classified by stage: `*pixelized*` images -> PIXELIZATION, other images -> IMAGE, assets -> POST_PROCESSING

## Test Steps

- Case 1 (happy path): Directory with mixed artifacts - pixelized images, regular images, and assets are correctly classified
- Case 2 (edge case): Empty output directory returns no artifacts
- Case 3 (edge case): Missing subdirectories don't cause errors
- Case 4: Only non-pixelized images in images/ directory
- Case 5: Only pixelized images in images/ directory
- Case 6: Case-insensitive matching of 'pixelized' pattern

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
