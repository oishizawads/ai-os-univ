# expA001_baseline result

## Experiment ID
expA001_baseline

## Objective
Near-infrared challenge baseline with species-grouped validation.

## Validation
GroupKFold(n_splits=5, groups=species_number)

## Seed
42

## Model / Preprocessing
Ridge(alpha=1.0) / raw

## Fold Scores
- Fold 1: 18.864660
- Fold 2: 24.046491
- Fold 3: 44.494499
- Fold 4: 73.755494
- Fold 5: 14.987851

## Mean / Std
- Mean RMSE: 35.229799
- Std RMSE: 21.783868
- Overall OOF RMSE: 42.443475

## Findings
- A plain Ridge baseline runs successfully with grouped validation by `species_number`.
- Performance varies sharply by held-out species group, indicating strong domain shift across species.

## Failure Modes
- Fold 4 is substantially worse than the others, so some held-out species groups are much harder to generalize to.
- Raw spectra with a linear model likely underfit species-specific structure.

## Next Hypothesis
Try spectrum preprocessing and stronger regularized models while keeping `GroupKFold(species_number)` fixed.
