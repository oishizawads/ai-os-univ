import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_squared_error
from scipy.signal import savgol_filter
import warnings
warnings.filterwarnings('ignore')

train = pd.read_csv('C:/workspace/ai-os/competitions/near-infrared-challenge/data/raw/train.csv', encoding='cp932')
target_col = train.columns[3]
spectral_cols = train.columns[4:].tolist()
X_raw = train[spectral_cols].values.astype(float)
y = train[target_col].values.astype(float)
groups = train['species number'].values


def preprocess(X, method, ref_mean=None):
    if method == 'raw':
        return X.copy()
    elif method == 'snv':
        mu = X.mean(axis=1, keepdims=True)
        sd = X.std(axis=1, keepdims=True) + 1e-10
        return (X - mu) / sd
    elif method == 'sg1':
        return np.apply_along_axis(
            lambda x: savgol_filter(x, window_length=11, polyorder=2, deriv=1), 1, X)
    elif method == 'snv_sg1':
        mu = X.mean(axis=1, keepdims=True)
        sd = X.std(axis=1, keepdims=True) + 1e-10
        Xs = (X - mu) / sd
        return np.apply_along_axis(
            lambda x: savgol_filter(x, window_length=11, polyorder=2, deriv=1), 1, Xs)
    elif method == 'msc':
        if ref_mean is None:
            ref_mean = X.mean(axis=0)
        out = np.zeros_like(X)
        for i in range(len(X)):
            coef = np.polyfit(ref_mean, X[i], 1)
            out[i] = (X[i] - coef[1]) / (coef[0] + 1e-10)
        return out
    return X.copy()


logo = LeaveOneGroupOut()
preprocessings = ['raw', 'snv', 'sg1', 'snv_sg1', 'msc']
ks = [3, 5, 10, 20, 50]
metrics = ['euclidean', 'cosine']
weights = ['uniform', 'distance']

results = []
total = len(preprocessings) * len(ks) * len(metrics) * len(weights)
done = 0

for prep in preprocessings:
    # preprocess full train for MSC ref
    X_ref_mean = X_raw.mean(axis=0) if prep == 'msc' else None

    for k in ks:
        for metric in metrics:
            for weight in weights:
                oof = np.zeros(len(y))
                fold_rmses = []

                for train_idx, val_idx in logo.split(X_raw, y, groups):
                    X_tr_raw, X_val_raw = X_raw[train_idx], X_raw[val_idx]
                    y_tr = y[train_idx]

                    ref = X_tr_raw.mean(axis=0) if prep == 'msc' else None
                    X_tr = preprocess(X_tr_raw, prep, ref)
                    X_val = preprocess(X_val_raw, prep, ref)

                    knn = KNeighborsRegressor(n_neighbors=min(k, len(X_tr)), metric=metric, weights=weight)
                    knn.fit(X_tr, y_tr)
                    pred = knn.predict(X_val)
                    oof[val_idx] = pred
                    fold_rmses.append(np.sqrt(mean_squared_error(y[val_idx], pred)))

                oof_rmse = np.sqrt(mean_squared_error(y, oof))
                results.append({
                    'preprocessing': prep, 'k': k, 'metric': metric, 'weight': weight,
                    'loso_oof_rmse': oof_rmse,
                    'loso_fold_mean': np.mean(fold_rmses),
                    'loso_fold_std': np.std(fold_rmses)
                })
                done += 1
                if done % 20 == 0:
                    print(f'  progress: {done}/{total}')

df = pd.DataFrame(results).sort_values('loso_oof_rmse')
df.to_csv('C:/workspace/ai-os/competitions/near-infrared-challenge/experiments/expKNN_grid/results.csv', index=False)

print('\n=== Top 10 KNN configurations (LOSO) ===')
print(df.head(10).to_string(index=False))

print('\n=== Best config fold breakdown ===')
best = df.iloc[0]
print(f"prep={best['preprocessing']}, k={best['k']}, metric={best['metric']}, weight={best['weight']}")
print(f"LOSO OOF RMSE={best['loso_oof_rmse']:.4f}, fold_mean={best['loso_fold_mean']:.4f}, fold_std={best['loso_fold_std']:.4f}")
