# expA024_strong_batch

| rank | experiment_id | theme | validation | oof_rmse | fold_mean | fold_std |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | expA024_ipls_pls | iPLS-style interval selection + PLS | GroupKFold_species | 25.234007 | 24.070117 | 8.184427 |
| 2 | expA025_water_band_pls | Water-band-focused interval + PLS | GroupKFold_species | 25.736486 | 24.907103 | 6.792689 |
| 3 | expA026_cars_like_pls | CARS-like selection + PLS | GroupKFold_species | 29.430584 | 28.304099 | 7.737526 |
| 4 | expA028_preproc_ensemble_pls | Raw/SG1/SG2 PLS ensemble | GroupKFold_species | 29.575054 | 25.450258 | 15.794961 |
| 5 | expA027_loso_sg1_pls | SG1 + PLS with LOSO | LeaveOneGroupOut_species | 36.376932 | 30.393779 | 18.926551 |