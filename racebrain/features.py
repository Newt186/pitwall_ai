import pandas as pd
import numpy as np
import os

# Load data

df = pd.read_csv('data/processed/all_laps.csv')

# Sort properly

df = df.sort_values([
    'Year',
    'EventName',
    'Driver',
    'LapNumber'
])

# TARGET VARIABLE

df['pit_next_lap'] = (
    df.groupby(['Year', 'EventName', 'Driver'])['PitInTime']
    .shift(-1)
    .notnull()
    .astype(int)
)

# FEATURE 1 — rolling average

df['rolling_avg_3'] = (
    df.groupby(['Year', 'EventName', 'Driver'])['LapTime_s']
    .transform(lambda x: x.rolling(3).mean())
)

# FEATURE 2 — degradation rate

df['deg_rate'] = (
    df['LapTime_s'] - df['rolling_avg_3']
)

# FEATURE 3 — gap ahead

df = df.sort_values([
    'Year',
    'EventName',
    'LapNumber',
    'Position'
])

# Approximate time gap

df['gap_ahead'] = (
    df.groupby([
        'Year',
        'EventName',
        'LapNumber'
    ])['LapTime_s']
    .diff()
    .abs()
)

# Fill leader gap

df['gap_ahead'] = df['gap_ahead'].fillna(999)

# FEATURE 4 — undercut risk

df['undercut_risk'] = (
    (df['gap_ahead'] < 22) &
    (df['TyreLife'] > 12)
).astype(int)

# FEATURE 5 — compound encoding

compound_map = {
    'SOFT': 0,
    'MEDIUM': 1,
    'HARD': 2
}

df['Compound'] = df['Compound'].map(compound_map)

# Final features

final_cols = [
    'LapNumber',
    'TyreLife',
    'Compound',
    'deg_rate',
    'gap_ahead',
    'undercut_risk',
    'Position',
    'pit_next_lap',
    'Year',
    'EventName',
    'Driver'
]

df = df[final_cols]

# Remove nulls

df = df.dropna()

# Save features

output_path = 'data/processed/features.csv'

df.to_csv(output_path, index=False)

print("Features saved successfully")
print(df.columns)
print(df['pit_next_lap'].value_counts())
