import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.neighbors import NearestNeighbors
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
    elif method == 'snv_sg1':
        mu = X.mean(axis=1, keepdims=True)
        sd = X.std(axis=1, keepdims=True) + 1e-10
        Xs = (X - mu) / sd
        return np.apply_along_axis(
            lambda x: savgol_filter(x, window_length=11, polyorder=2, deriv=1), 1, Xs)
    return X.copy()


def predict_local_pls(X_tr, y_tr, X_val, k, n_comp):
    nn = NearestNeighbors(n_neighbors=min(k, len(X_tr)), metric='euclidean')
    nn.fit(X_tr)
    indices = nn.kneighbors(X_val, return_distance=False)
    preds = []
    for i, idx in enumerate(indices):
        X_local = X_tr[idx]
        y_local = y_tr[idx]
        nc = min(n_comp, len(idx) - 1, 20)
        if nc < 1:
            preds.append(y_local.mean())
            continue
        pls = PLSRegression(n_components=nc)
        pls.fit(X_local, y_local)
        pred = pls.predict(X_val[i:i+1])
        preds.append(float(np.ravel(pred)[0]))
    return np.array(preds)


logo = LeaveOneGroupOut()
preprocessings = ['raw', 'snv', 'snv_sg1']
ks = [50, 100, 200, 400]
n_comps = [5, 10, 15]

results = []
total = len(preprocessings) * len(ks) * len(n_comps)
done = 0

for prep in preprocessings:
    for k in ks:
        for n_comp in n_comps:
            oof = np.zeros(len(y))
            fold_rmses = []

            for train_idx, val_idx in logo.split(X_raw, y, groups):
                X_tr_raw, X_val_raw = X_raw[train_idx], X_raw[val_idx]
                y_tr = y[train_idx]

                X_tr = preprocess(X_tr_raw, prep)
                X_val = preprocess(X_val_raw, prep)

                pred = predict_local_pls(X_tr, y_tr, X_val, k, n_comp)
                oof[val_idx] = pred
                fold_rmses.append(np.sqrt(mean_squared_error(y[val_idx], pred)))

            oof_rmse = np.sqrt(mean_squared_error(y, oof))
            results.append({
                'preprocessing': prep, 'k': k, 'n_components': n_comp,
                'loso_oof_rmse': oof_rmse,
                'loso_fold_mean': np.mean(fold_rmses),
                'loso_fold_std': np.std(fold_rmses)
            })
            done += 1
            print(f'[{done}/{total}] prep={prep}, k={k}, n_comp={n_comp} -> RMSE={oof_rmse:.4f}')

df = pd.DataFrame(results).sort_values('loso_oof_rmse')
df.to_csv('C:/workspace/ai-os/competitions/near-infrared-challenge/experiments/expLocalPLS/results.csv', index=False)

print('\n=== Top 10 LocalPLS configurations (LOSO) ===')
print(df.head(10).to_string(index=False))
