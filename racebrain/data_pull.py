import fastf1
import pandas as pd
import os

# Enable cache

os.makedirs('data/f1_cache', exist_ok=True)

fastf1.Cache.enable_cache('data/f1_cache')

all_laps = []

years = [2022, 2023, 2024]

for year in years:

    print(f"\nLoading {year} season...")

    for rnd in range(1, 23):

        try:
            session = fastf1.get_session(year, rnd, 'R')

            session.load()

            laps = session.laps.copy()

            laps['Year'] = year
            laps['EventName'] = session.event['EventName']

            keep_cols = [
                'LapNumber',
                'Driver',
                'Compound',
                'TyreLife',
                'LapTime',
                'Position',
                'PitInTime',
                'PitOutTime',
                'Year',
                'EventName'
            ]

            laps = laps[keep_cols]

            all_laps.append(laps)

            print(f"Loaded {year} Round {rnd}")

        except Exception as e:
            print(f"Skipped {year} Round {rnd}: {e}")

# Combine all races

df = pd.concat(all_laps, ignore_index=True)

# Convert lap time to seconds

df['LapTime_s'] = df['LapTime'].dt.total_seconds()

# Remove invalid rows

df = df.dropna(subset=['LapTime_s'])

df = df[df['LapTime_s'] < 200]

# Save dataset

os.makedirs('data/processed', exist_ok=True)

output_path = 'data/processed/all_laps.csv'

df.to_csv(output_path, index=False)

print(f"Saved {len(df)} rows to all_laps.csv")
