---
experiment_id: expA053_optuna_all
date: 2026-04-02
author: Claude (PM)
---

# Design: Multi-model Optuna HPO (expA053)

## Goal
band2+SNV/SNV+SG1 上でできる限り多くのモデルをOptunaでチューニングし、
各モデルの最良LOSO RMSEを取得する。アンサンブル候補の洗い出しが目的。

## CV
- LeaveOneGroupOut (groups=species_number)
- 13 folds
- objective: RMSE with clip(>=0)

## Features
- band2 (4800-5350 cm⁻¹, 約100特徴量)
- preprocessing: snv, snv_sg1

## Models
| model | n_trials |
|-------|---------|
| lgbm | 80 |
| xgb | 80 |
| catboost | 80 |
| histgbm | 80 |
| ridge | 100 |
| elasticnet | 100 |
| svr | 50 |
| kernelridge | 50 |
| rf | 60 |
| et | 60 |
| pls | 50 |

## Output
- `results.csv`: model, preproc, loso_rmse (sorted)
- `best_params/{model}_{preproc}.json`: best hyperparams
- `trials/{model}_{preproc}.csv`: all trial history
- `submissions/expA053_{model}_{preproc}_submission.csv`: test predictions

## Constraints
- 既存実験ファイルは一切変更しない
- seed=42 固定
- test予測はclip(>=0)
