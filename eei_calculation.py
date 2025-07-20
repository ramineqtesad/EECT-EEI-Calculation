# eei_calculation.py
# Python script for calculating the Ecological Entropy Index (EEI) and statistical analyses

import pandas as pd
import numpy as np
from scipy.stats import shapiro
from SALib.sample import saltelli
from SALib.analyze import sobol
import xgboost as xgb
from shap import TreeExplainer
import matplotlib.pyplot as plt

# Sample data based on Table 1
data = {
    'Year': [1990, 2024, 2020, 2020, 2020],
    'Location': ['Urmia', 'Urmia', 'Aral Sea', 'Pantanal', 'Mekong Delta'],
    'Salinity': [200, 310, 120, np.nan, np.nan],
    'Biodiversity': [2.5, 1.1, 0.8, 1.5, 1.3],
    'Energy_Flow': [800, 1200, 950, 900, 1000]
}
df = pd.DataFrame(data)

# Normalize data to [0, 10]
def normalize(series, max_val):
    return (series / max_val) * 10

df['Salinity_Norm'] = normalize(df['Salinity'].fillna(0), max_val=310)
df['Biodiversity_Norm'] = normalize(df['Biodiversity'], max_val=2.5)
df['Energy_Flow_Norm'] = normalize(df['Energy_Flow'], max_val=1200)

# Calculate Shannon Entropy (H) for biodiversity
def shannon_entropy(biodiversity):
    p = biodiversity / biodiversity.sum()  # Assuming biodiversity is a proxy for species distribution
    return -np.sum(p * np.log(p + 1e-10))  # Add small value to avoid log(0)

df['Shannon_Entropy'] = df['Biodiversity'].apply(shannon_entropy)

# EEI calculation: EEI = H + 0.5S + 0.3B + 0.2E
def calculate_eei(row):
    return row['Shannon_Entropy'] + 0.5 * row['Salinity_Norm'] + 0.3 * row['Biodiversity_Norm'] + 0.2 * row['Energy_Flow_Norm']

df['EEI'] = df.apply(calculate_eei, axis=1)

# Sobol Sensitivity Analysis
problem = {
    'num_vars': 3,
    'names': ['Salinity', 'Biodiversity', 'Energy_Flow'],
    'bounds': [[0, 10], [0, 10], [0, 10]]
}
param_values = saltelli.sample(problem, 10000)
Y = np.array([calculate_eei({'Shannon_Entropy': 1, 'Salinity_Norm': p[0], 'Biodiversity_Norm': p[1], 'Energy_Flow_Norm': p[2]}) for p in param_values])
sobol_indices = sobol.analyze(problem, Y)
print("Sobol Indices (First-order):", sobol_indices['S1'])

# SHAP Analysis with XGBoost
X = df[['Salinity_Norm', 'Biodiversity_Norm', 'Energy_Flow_Norm']].fillna(0)
y = df['EEI']
model = xgb.XGBRegressor().fit(X, y)
explainer = TreeExplainer(model)
shap_values = explainer.shap_values(X)
print("SHAP Values:", shap_values)

# CUSUM Algorithm for Threshold Detection
def cusum(data, threshold=5.0, mean_window=10):
    mean = data.rolling(window=mean_window).mean()
    s_pos = np.zeros(len(data))
    s_neg = np.zeros(len(data))
    for i in range(1, len(data)):
        s_pos[i] = max(0, s_pos[i-1] + data[i] - mean[i] - threshold)
        s_neg[i] = max(0, s_neg[i-1] + mean[i] - data[i] - threshold)
    return s_pos, s_neg

s_pos, s_neg = cusum(df['EEI'], threshold=5.0)
df['CUSUM_Pos'] = s_pos
df['CUSUM_Neg'] = s_neg

# Normality Test (Shapiro-Wilk)
stat, p_value = shapiro(df['EEI'])
print(f"Shapiro-Wilk Test: Statistic={stat:.3f}, p-value={p_value:.3f}")

# Save results to CSV
df.to_csv('eei_results.csv', index=False)

# Plot EEI Trend (Figure 5)
plt.figure(figsize=(10, 6))
plt.plot(df[df['Location'] == 'Urmia']['Year'], df[df['Location'] == 'Urmia']['EEI'], marker='o')
plt.fill_between(df[df['Location'] == 'Urmia']['Year'], 
                 df[df['Location'] == 'Urmia']['EEI'] - 0.2, 
                 df[df['Location'] == 'Urmia']['EEI'] + 0.2, alpha=0.2)
plt.title('EEI Trend for Lake Urmia (1990–2024)')
plt.xlabel('Year')
plt.ylabel('EEI')
plt.savefig('Figure5_EEI_Trend.png', dpi=300)
plt.close()

# Plot Scatter (Figure 6)
plt.figure(figsize=(10, 6))
plt.scatter(df['Salinity'].fillna(0), df['Biodiversity'], c=df['EEI'], cmap='viridis')
plt.colorbar(label='EEI')
plt.xlabel('Salinity (g/L)')
plt.ylabel('Biodiversity (Shannon Index)')
plt.title('Salinity vs. Biodiversity vs. EEI')
plt.savefig('Figure6_Scatter.png', dpi=300)
plt.close()
