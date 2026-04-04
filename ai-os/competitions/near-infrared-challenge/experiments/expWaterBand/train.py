import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_squared_error
from scipy.signal import savgol_filter
import warnings
warnings.filterwarnings('ignore')

train = pd.read_csv('C:/workspace/ai-os/competitions/near-infrared-challenge/data/raw/train.csv', encoding='cp932')
target_col = train.columns[3]
spectral_cols = train.columns[4:].tolist()
wn = np.array([float(c) for c in spectral_cols])
X_raw = train[spectral_cols].values.astype(float)
y = train[target_col].values.astype(float)
groups = train['species number'].values

# Water absorption bands (cm-1)
bands = {
    'band1_OH_overtone': (6700, 7400),   # ~1351-1493nm
    'band2_OH_combination': (4800, 5350), # ~1869-2083nm
    'band3_OH_bend_stretch': (4200, 4700), # ~2128-2381nm
}
band_masks = {name: (wn >= lo) & (wn <= hi) for name, (lo, hi) in bands.items()}
all_water_mask = band_masks['band1_OH_overtone'] | band_masks['band2_OH_combination'] | band_masks['band3_OH_bend_stretch']
band_masks['all_water'] = all_water_mask
band_masks['full'] = np.ones(len(wn), dtype=bool)

print('Band sizes:')
for name, mask in band_masks.items():
    print(f'  {name}: {mask.sum()} wavelengths')


def snv(X):
    mu = X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, keepdims=True) + 1e-10
    return (X - mu) / sd


logo = LeaveOneGroupOut()
results = []

for band_name, mask in band_masks.items():
    X_band = X_raw[:, mask]
    X_band_snv = snv(X_band)

    for prep_name, X in [('raw', X_band), ('snv', X_band_snv)]:
        # PLS
        for n_comp in [5, 10, 15]:
            if n_comp >= mask.sum():
                continue
            oof = np.zeros(len(y))
            fold_rmses = []
            for tr_idx, val_idx in logo.split(X, y, groups):
                pls = PLSRegression(n_components=min(n_comp, len(tr_idx) - 1))
                pls.fit(X[tr_idx], y[tr_idx])
                pred = pls.predict(X[val_idx]).ravel()
                oof[val_idx] = pred
                fold_rmses.append(np.sqrt(mean_squared_error(y[val_idx], pred)))
            oof_rmse = np.sqrt(mean_squared_error(y, oof))
            results.append({'band': band_name, 'preprocessing': prep_name, 'model': f'PLS_n{n_comp}',
                            'loso_oof_rmse': oof_rmse, 'fold_mean': np.mean(fold_rmses), 'fold_std': np.std(fold_rmses)})
            print(f'  {band_name}/{prep_name}/PLS_n{n_comp}: {oof_rmse:.4f}')

        # KNN
        for k in [5, 10, 20]:
            oof = np.zeros(len(y))
            fold_rmses = []
            for tr_idx, val_idx in logo.split(X, y, groups):
                knn = KNeighborsRegressor(n_neighbors=min(k, len(tr_idx)), metric='euclidean', weights='distance')
                knn.fit(X[tr_idx], y[tr_idx])
                pred = knn.predict(X[val_idx])
                oof[val_idx] = pred
                fold_rmses.append(np.sqrt(mean_squared_error(y[val_idx], pred)))
            oof_rmse = np.sqrt(mean_squared_error(y, oof))
            results.append({'band': band_name, 'preprocessing': prep_name, 'model': f'KNN_k{k}',
                            'loso_oof_rmse': oof_rmse, 'fold_mean': np.mean(fold_rmses), 'fold_std': np.std(fold_rmses)})
            print(f'  {band_name}/{prep_name}/KNN_k{k}: {oof_rmse:.4f}')

df = pd.DataFrame(results).sort_values('loso_oof_rmse')
df.to_csv('C:/workspace/ai-os/competitions/near-infrared-challenge/experiments/expWaterBand/results.csv', index=False)

print('\n=== Top 15 results ===')
print(df.head(15).to_string(index=False))

print('\n=== Full band vs water band comparison (best per band) ===')
for band in df['band'].unique():
    best = df[df['band'] == band].iloc[0]
    print(f"  {band:30s}: best RMSE={best['loso_oof_rmse']:.4f} ({best['preprocessing']}/{best['model']})")
