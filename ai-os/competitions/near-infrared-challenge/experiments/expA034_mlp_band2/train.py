from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
EPOCHS = 200
BATCH_SIZE = 64
LR = 1e-3
PATIENCE = 20


class MLP(nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64),  nn.BatchNorm1d(64),  nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 1),
        )
    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_mlp(X_tr: np.ndarray, y_tr: np.ndarray) -> tuple[MLP, StandardScaler]:
    scaler = StandardScaler()
    X_s = scaler.fit_transform(X_tr).astype(np.float32)
    y_s = y_tr.astype(np.float32)

    model = MLP(X_s.shape[1]).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    loss_fn = nn.MSELoss()

    X_t = torch.tensor(X_s, device=DEVICE)
    y_t = torch.tensor(y_s, device=DEVICE)

    best_loss, patience_count, best_state = float("inf"), 0, None
    n = len(X_t)

    for epoch in range(EPOCHS):
        model.train()
        idx = torch.randperm(n, device=DEVICE)
        epoch_loss = 0.0
        for i in range(0, n, BATCH_SIZE):
            b = idx[i:i + BATCH_SIZE]
            opt.zero_grad()
            loss = loss_fn(model(X_t[b]), y_t[b])
            loss.backward()
            opt.step()
            epoch_loss += loss.item() * len(b)
        scheduler.step()
        epoch_loss /= n
        if epoch_loss < best_loss:
            best_loss, patience_count = epoch_loss, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_count += 1
            if patience_count >= PATIENCE:
                break

    model.load_state_dict(best_state)
    return model, scaler


def predict_mlp(model: MLP, scaler: StandardScaler, X: np.ndarray) -> np.ndarray:
    model.eval()
    X_s = scaler.transform(X).astype(np.float32)
    with torch.no_grad():
        preds = model(torch.tensor(X_s, device=DEVICE)).cpu().numpy()
    return preds


SETTINGS = [
    ("snv_mlp",     apply_snv),
    ("snv_sg1_mlp", apply_snv_sg1),
]


def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut()
    print(f"band2_features={len(band2_cols)}, device={DEVICE}")

    results = []
    best_rmse, best_name, best_preproc_fn = float("inf"), None, None

    for name, preproc_fn in SETTINGS:
        Xp = preproc_fn(X)
        oof = np.zeros_like(y, dtype=np.float64)
        torch.manual_seed(42)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            model, scaler = train_mlp(Xp[tr], y[tr])
            oof[val] = predict_mlp(model, scaler, Xp[val])
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse})
        print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse:
            best_rmse, best_name, best_preproc_fn = rmse, name, preproc_fn

    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))

    Xp_all = best_preproc_fn(X)
    Xp_test = best_preproc_fn(X_test)
    torch.manual_seed(42)
    model, scaler = train_mlp(Xp_all, y)
    preds = predict_mlp(model, scaler, Xp_test)
    print(f"\nbest={best_name} loso={best_rmse:.6f} pred_min={preds.min():.4f} pred_max={preds.max():.4f}")
    if np.any(preds < 0):
        print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR / f"expA034_mlp_{best_name}_submission.csv")
    print(f"saved_submission=expA034_mlp_{best_name}_submission.csv")

if __name__ == "__main__":
    main()
