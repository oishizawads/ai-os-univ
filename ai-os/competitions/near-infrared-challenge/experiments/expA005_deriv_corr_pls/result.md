# expA005_deriv_corr_pls

## Configuration

- Validation: GroupKFold by `species_number` (`n_splits=5`)
- Model: `PLSRegression`
- Preprocessing: Savitzky-Golay 1st derivative (`window=11`, `polyorder=2`, `deriv=1`)
- Feature selection: absolute correlation top-k on training folds

## Sweep Table

| n_top_features | n_components | OOF RMSE | fold RMSE mean | fold RMSE std |
| ---: | ---: | ---: | ---: | ---: |
| 50 | 3 | 33.599968 | 31.239324 | 13.076699 |
| 50 | 5 | 29.458621 | 28.433130 | 8.377531 |
| 50 | 8 | 29.223530 | 27.971180 | 8.857681 |
| 50 | 10 | 28.340349 | 27.497039 | 7.741197 |
| 50 | 15 | 28.271710 | 27.531022 | 7.265819 |
| 50 | 20 | 29.112081 | 28.494337 | 6.616526 |
| 100 | 3 | 33.078505 | 31.041017 | 12.254793 |
| 100 | 5 | 32.782529 | 30.658158 | 12.478905 |
| 100 | 8 | 29.217071 | 27.361215 | 11.212967 |
| 100 | 10 | 26.472628 | 25.432518 | 8.246848 |
| 100 | 15 | 24.365418 | 23.710453 | 6.093789 |
| 100 | 20 | 25.769059 | 24.759894 | 6.749982 |
| 200 | 3 | 27.289919 | 25.964493 | 9.570436 |
| 200 | 5 | 32.304602 | 28.861588 | 15.526382 |
| 200 | 10 | 38.081148 | 33.286180 | 19.005005 |
| 200 | 15 | 38.953381 | 34.557103 | 17.592933 |
| 200 | 20 | 63.745346 | 49.427761 | 40.927535 |
| 400 | 3 | 34.139657 | 31.001800 | 15.055541 |
| 400 | 5 | 35.263692 | 30.623648 | 18.608748 |
| 400 | 8 | 90.012263 | 55.859647 | 72.359260 |
| 400 | 10 | 93.078259 | 58.548853 | 74.220554 |
| 400 | 15 | 48.746738 | 36.973203 | 32.788339 |
| 400 | 20 | 53.608363 | 39.584168 | 37.243992 |
| 700 | 3 | 38.769171 | 34.859039 | 17.297433 |
| 700 | 5 | 48.393436 | 38.008043 | 31.136892 |
| 700 | 8 | 99.226426 | 65.891094 | 75.894723 |
| 700 | 10 | 122.074805 | 81.546825 | 92.739569 |
| 700 | 15 | 68.217321 | 56.978689 | 36.115061 |
| 700 | 20 | 59.140648 | 49.739685 | 30.897514 |

## Best Configuration

- best n_top_features: 100
- best n_components: 15
- best OOF RMSE: 24.365418
- prepared test matrix shape: `(550, 100)`

## Notes

- Top-100 correlation filtering was clearly more stable than using 400 or 700 features.
- Higher component counts became unstable once too many features were retained.
- This experiment is submission-ready via `submissions/expA005_deriv_corr_pls_submission.csv`.
