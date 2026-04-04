# expA010_research_batch12

## Ranking

| rank | experiment_id | theme | validation | oof_rmse | fold_mean | fold_std |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | expA017_ipls_pls | iPLS-style interval selection + PLS | GroupKFold_species | 25.234007 | 24.070117 | 8.184427 |
| 2 | expA018_water_band_pls | Water-band-focused interval + PLS | GroupKFold_species | 25.736486 | 24.907103 | 6.792689 |
| 3 | expA016_cars_like_pls | CARS-like selection + PLS | GroupKFold_species | 31.030764 | 29.437752 | 9.654120 |
| 4 | expA013_detrend_pls | Detrending + PLS | GroupKFold_species | 32.532165 | 30.448548 | 13.087975 |
| 5 | expA019_elasticnet_preproc | Elastic Net with preprocessing variants | GroupKFold_species | 47.017828 | 38.649895 | 24.825851 |
| 6 | expA020_logo_eval | Leave-One-Species-Out evaluation | LeaveOneGroupOut_species | 48.310620 | 38.313717 | 29.155199 |
| 7 | expA011_snv_sg_pls | SNV + SG derivative + PLS | GroupKFold_species | 53.394907 | 39.721766 | 36.526199 |
| 8 | expA014_sg_param_pls | SG parameter sweep + PLS | GroupKFold_species | 54.433288 | 40.555987 | 37.387969 |
| 9 | expA022_species_aware_hierarchical | Species-aware local or hierarchical modeling | GroupKFold_species | 67.058856 | 56.846267 | 33.513521 |
| 10 | expA015_vip_pls | VIP selection + PLS | GroupKFold_species | 68.651192 | 58.521366 | 34.603871 |
| 11 | expA012_msc_sg_pls | MSC + SG derivative + PLS | GroupKFold_species | 82.400463 | 53.505537 | 64.169317 |

## Non-OOF Items

- `expA021_blend`: submission-only ensemble of existing strong submissions

## Files

- summary csv: `C:\workspace\competitions\near-infrared-challenge\experiments\expA010_research_batch12\summary.csv`