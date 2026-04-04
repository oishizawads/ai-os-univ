# expA004_snv_pls

## Sweep Table

| n_components | OOF RMSE | fold RMSE mean | fold RMSE std |
| ---: | ---: | ---: | ---: |
| 3 | 27.847695 | 24.978956 | 12.477950 |
| 5 | 48.492937 | 37.387539 | 31.634021 |
| 8 | 73.439288 | 48.569827 | 56.521473 |
| 10 | 95.207071 | 69.239937 | 66.450481 |
| 12 | 173.333803 | 112.997654 | 134.205370 |
| 15 | 309.986111 | 179.051316 | 258.767899 |
| 20 | 208.366169 | 126.478433 | 169.493853 |

## Best Configuration

- best n_components: 3
- final OOF RMSE: 27.847695

## Comparison vs Ridge Baseline

- Ridge baseline OOF RMSE: 42.44
- SNV + PLS OOF RMSE: 27.847695
- Improvement: 14.592305 RMSE lower than the Ridge baseline
