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
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
EPOCHS, BATCH, LR, PATIENCE = 300, 32, 1e-3, 30

class CNN1D(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=7, padding=3), nn.BatchNorm1d(32), nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=5, padding=2), nn.BatchNorm1d(64), nn.ReLU(),
            nn.AdaptiveAvgPool1d(16),
        )
        self.fc = nn.Sequential(
            nn.Linear(64*16, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 1)
        )
    def forward(self, x):
        x = x.unsqueeze(1)
        return self.fc(self.conv(x).flatten(1)).squeeze(-1)

def train_model(X_tr, y_tr):
    sc = StandardScaler(); Xs = sc.fit_transform(X_tr).astype(np.float32)
    ys = y_tr.astype(np.float32)
    model = CNN1D(Xs.shape[1]).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    loss_fn = nn.MSELoss()
    Xt = torch.tensor(Xs, device=DEVICE); yt = torch.tensor(ys, device=DEVICE)
    best_loss, pat, best_state = float("inf"), 0, None
    for ep in range(EPOCHS):
        model.train()
        idx = torch.randperm(len(Xt), device=DEVICE)
        el = 0.0
        for i in range(0, len(Xt), BATCH):
            b = idx[i:i+BATCH]; opt.zero_grad()
            loss = loss_fn(model(Xt[b]), yt[b]); loss.backward(); opt.step()
            el += loss.item()*len(b)
        sched.step(); el /= len(Xt)
        if el < best_loss: best_loss, pat, best_state = el, 0, {k: v.clone() for k,v in model.state_dict().items()}
        else:
            pat += 1
            if pat >= PATIENCE: break
    model.load_state_dict(best_state)
    return model, sc

def predict(model, sc, X):
    model.eval()
    Xs = sc.transform(X).astype(np.float32)
    with torch.no_grad(): return model(torch.tensor(Xs, device=DEVICE)).cpu().numpy()

SETTINGS = [("snv_cnn", apply_snv), ("snv_sg1_cnn", apply_snv_sg1)]

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64); y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy(); X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut(); print(f"device={DEVICE} band2={len(band2_cols)}")
    results = []; best_rmse, best_name, best_pfn = float("inf"), None, None
    for name, pfn in SETTINGS:
        Xp = pfn(X); oof = np.zeros_like(y, dtype=np.float64)
        torch.manual_seed(42)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            m, sc = train_model(Xp[tr], y[tr]); oof[val] = predict(m, sc, Xp[val])
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse}); print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse: best_rmse, best_name, best_pfn = rmse, name, pfn
    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))
    Xp_all = best_pfn(X); Xp_test = best_pfn(X_test)
    torch.manual_seed(42); m, sc = train_model(Xp_all, y); preds = predict(m, sc, Xp_test)
    print(f"\nbest={best_name} loso={best_rmse:.6f} min={preds.min():.4f} max={preds.max():.4f}")
    if np.any(preds < 0): print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR/f"expA038_cnn_{best_name}_submission.csv")
    print(f"saved_submission=expA038_cnn_{best_name}_submission.csv")

if __name__ == "__main__": main()
