# Releasing Question Generation Engine

This project follows [Semantic Versioning](https://semver.org/).

## Release Process

1. **Update Documentation**
   - Ensure `README.md` and `CHANGELOG.md` (if applicable) are up to date.

2. **Run Tests**
   - Ensure all tests pass locally and in CI.

3. **Tag the Release**
   - We use git tags to trigger releases.
   - Tag format: `vX.Y.Z` (e.g., `v1.0.0`).

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0: Initial public release"
   git push origin v1.0.0
   ```

4. **GitHub Action**
   - Pushing the tag will trigger the `release.yml` workflow.
   - This workflow will automatically:
     - Build the project (if applicable).
     - Create a GitHub Release.
     - Attach any build artifacts.

## Versioning Strategy

- **Major (X.y.z)**: Breaking changes.
- **Minor (x.Y.z)**: New features (backward compatible).
- **Patch (x.y.Z)**: Bug fixes (backward compatible).
