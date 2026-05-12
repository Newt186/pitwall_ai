import pandas as pd
import numpy as np
import joblib

pit_model = joblib.load('models/pit_model.pkl')
pos_model = joblib.load('models/pos_model.pkl')

features = [
    'LapNumber',
    'TyreLife',
    'Compound',
    'deg_rate',
    'gap_ahead',
    'undercut_risk',
    'Position'
]

def predict_pit(lap, tyre_life, compound, deg_rate, gap_ahead, undercut_risk, position):
    sample = pd.DataFrame([{
        'LapNumber': lap,
        'TyreLife': tyre_life,
        'Compound': compound,
        'deg_rate': deg_rate,
        'gap_ahead': gap_ahead,
        'undercut_risk': undercut_risk,
        'Position': position
    }])
    probability = pit_model.predict_proba(sample)[0][1]
    return {
        'probability': round(float(probability), 3),
        'recommended': probability > 0.60,
        'undercut_risk': undercut_risk
    }

def predict_position(lap, tyre_life, compound, deg_rate, gap_ahead, undercut_risk, position):
    sample = pd.DataFrame([{
        'LapNumber': lap,
        'TyreLife': tyre_life,
        'Compound': compound,
        'deg_rate': deg_rate,
        'gap_ahead': gap_ahead,
        'undercut_risk': undercut_risk,
        'Position': position
    }])
    predicted_position = pos_model.predict(sample)[0]
    predicted_position = round(predicted_position)
    predicted_position = max(1, min(20, predicted_position))
    return predicted_position

if __name__ == '__main__':
    df = pd.read_csv('data/processed/features.csv')
    bahrain = df[(df['Year'] == 2022)].copy()
    bahrain = bahrain.head(100)

    probabilities = []
    recommendations = []
    predicted_positions = []

    for _, row in bahrain.iterrows():
        pit_result = predict_pit(
            row['LapNumber'], row['TyreLife'], row['Compound'],
            row['deg_rate'], row['gap_ahead'], row['undercut_risk'], row['Position']
        )
        pos_result = predict_position(
            row['LapNumber'], row['TyreLife'], row['Compound'],
            row['deg_rate'], row['gap_ahead'], row['undercut_risk'], row['Position']
        )
        probabilities.append(pit_result['probability'])
        recommendations.append(pit_result['recommended'])
        predicted_positions.append(pos_result)

    bahrain['pit_probability'] = probabilities
    bahrain['recommended'] = recommendations
    bahrain['predicted_position'] = predicted_positions

    bahrain.to_csv('data/processed/bahrain_2024_demo.csv', index=False)
    print("Saved bahrain_2024_demo.csv")
