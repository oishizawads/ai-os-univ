# Current Result Mapping

## Executed From The Ledger

| ledger_id | theme | executed_by | status | key_result |
| --- | --- | --- | --- | --- |
| expA023 | Raw + PLS baseline | [expA001_baseline/train.py](/c:/workspace/competitions/near-infrared-challenge/experiments/expA001_baseline/train.py) | completed | OOF RMSE 42.443475 |

## Closest Existing Executions Already Available

| ledger_id | theme | closest existing experiment | status | key_result |
| --- | --- | --- | --- | --- |
| expA028 | Detrend + PLS | [expA013 result.md](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/result.md) | imported reference | OOF RMSE 32.532165 |
| expA036 | SG1 + VIP + PLS | [expA015_vip_pls row in summary.csv](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/summary.csv) | imported reference | OOF RMSE 68.651192 |
| expA037 | SG1 + CARS + PLS | [expA016_cars_like_pls row in summary.csv](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/summary.csv) | imported reference | OOF RMSE 31.030764 |
| expA038 | SG1 + iPLS | [expA017_ipls_pls row in summary.csv](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/summary.csv) | imported reference | OOF RMSE 25.234007 |
| expA039 | SG1 + water-band interval PLS | [expA018_water_band_pls row in summary.csv](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/summary.csv) | imported reference | OOF RMSE 25.736486 |
| expA040 | SG1 + PLS with LOSO | [expA020_logo_eval row in summary.csv](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/summary.csv) | imported reference | OOF RMSE 48.310620 |
| expA044 | Raw + Ridge | [expA001_baseline/train.py](/c:/workspace/competitions/near-infrared-challenge/experiments/expA001_baseline/train.py) | imported reference | OOF RMSE 42.443475 |
| expA045 | SG1 + Ridge | [expA008_deriv_ridge/train.py](/c:/workspace/competitions/near-infrared-challenge/experiments/expA008_deriv_ridge/train.py) | imported reference | OOF RMSE 42.848482 |
| expA046 | SNV + SG1 + Ridge | [expA009_snv_deriv_ridge/train.py](/c:/workspace/competitions/near-infrared-challenge/experiments/expA009_snv_deriv_ridge/train.py) | imported reference | OOF RMSE 48.378466 |
| expA047 | Raw + Elastic Net | [expA019_elasticnet_preproc row in summary.csv](/c:/workspace/competitions/near-infrared-challenge/experiments/expA010_research_batch12/summary.csv) | imported reference | best variant OOF RMSE 47.017828 |

## Interpretation

- The ledger itself has executed `1` item so far because only `expA023` had a concrete command.
- Several higher-value themes already have comparable results from earlier batch experiments.
- The strongest already-observed literature-aligned directions are:
  - `expA038` iPLS-style interval selection
  - `expA039` water-band-focused interval selection
  - `expA037` CARS-like selection
- The weakest among imported references were:
  - `expA036` VIP-based selection
  - `expA045` and `expA046` Ridge variants
