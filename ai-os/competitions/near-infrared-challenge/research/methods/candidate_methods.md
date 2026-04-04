# Candidate Methods

## Current Reading

- `PLS + wavelength selection` is still the strongest main line.
- `SNV`, `MSC`, `Savitzky-Golay derivative`, and their combinations are the most justified preprocessing families.
- Ridge is useful as a baseline, but current GroupKFold results suggest PLS-based models are more promising.
- Public LB instability means validation design and ensemble robustness matter as much as raw CV.

## Distinct Experiment Themes Worth Trying

1. `SNV + SG derivative + PLS`
2. `MSC + SG derivative + PLS`
3. `Detrending + PLS`
4. `SG parameter sweep + PLS`
5. `VIP selection + PLS`
6. `CARS selection + PLS`
7. `iPLS / siPLS / biPLS interval selection + PLS`
8. `Water-band-focused interval selection + PLS`
9. `Elastic Net with preprocessing variants`
10. `Leave-One-Species-Out evaluation`
11. `Blend / ensemble of strong submissions`
12. `Species-aware local or hierarchical modeling`

## Priority

### High Priority

- `VIP selection + PLS`
- `MSC + SG derivative + PLS`
- `SNV + SG derivative + PLS` with careful GroupKFold evaluation
- `Leave-One-Species-Out` as a diagnostic track
- Blend of `expA004`, `expA005`, and `expA008`
- `Nested GroupCV / LOSO` model selection
- `SG 2nd derivative + PLS`
- Stronger interval methods inspired by `iPLS`

### Medium Priority

- `CARS selection + PLS`
- `iPLS / siPLS / biPLS interval selection + PLS`
- `SG parameter sweep + PLS`
- `Water-band-focused interval selection + PLS`
- `Elastic Net` with the same preprocessing menu
- `Leave-Two-Species-Out` validation
- `PLS + Ridge` two-layer ensemble
- Spectral-cluster local models
- `di-PLS` style domain adaptation
- Tail-focused models for extreme moisture ranges

### Lower Priority

- Species-aware local or hierarchical modeling
- More complex nonlinear models without strong validation evidence

## Rejected Or Risky Directions

- Returning to plain `KFold` as the main validation
- Using `species_number` directly without a careful generalization story
- Increasing retained wavelengths blindly

## Notes From Current Experiments

- `expA005` and `expA006` indicate that around top-100 selected wavelengths is the best region so far.
- `expA007` to `expA009` suggest `SG derivative + Ridge` is the least bad Ridge variant, while `SNV + Ridge` is unstable.
- The main battlefield remains `PLS + better wavelength selection + safer validation`.
- `expA017` and `expA018` support interval-style selection more than simple pointwise ranking.
