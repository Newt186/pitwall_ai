import pandas as pd
import joblib

from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    confusion_matrix,
    mean_absolute_error
)

# Load data

df = pd.read_csv('data/processed/features.csv')

# Remove nulls

df = df.dropna()

# Train/test split

train_df = df[df['Year'].isin([2022, 2023])]

test_df = df[df['Year'] == 2024]

# Features

features = [
    'LapNumber',
    'TyreLife',
    'Compound',
    'deg_rate',
    'gap_ahead',
    'undercut_risk',
    'Position'
]

# =============================
# MODEL 1 — PIT STOP CLASSIFIER
# =============================

X_train = train_df[features]
y_train = train_df['pit_next_lap']

X_test = test_df[features]
y_test = test_df['pit_next_lap']

# Class imbalance ratio

ratio = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

print("Class imbalance ratio:", ratio)

# Train classifier

pit_model = XGBClassifier(
    objective='binary:logistic',
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    scale_pos_weight=ratio,
    random_state=42
)

pit_model.fit(X_train, y_train)

# Evaluate

predictions = pit_model.predict(X_test)

print(classification_report(y_test, predictions))
print("Precision:", precision_score(y_test, predictions))
print("Recall:", recall_score(y_test, predictions))
print(confusion_matrix(y_test, predictions))

# Save classifier

joblib.dump(pit_model, 'models/pit_model.pkl')

print("Saved pit_model.pkl")

# =============================
# MODEL 2 — POSITION PREDICTOR
# =============================

position_df = df[df['LapNumber'] > 20].copy()

# Create final position target

position_df['final_position'] = (
    position_df.groupby([
        'Year',
        'EventName',
        'Driver'
    ])['Position']
    .transform('last')
)

train_pos = position_df[position_df['Year'].isin([2022, 2023])]

test_pos = position_df[position_df['Year'] == 2024]

X_train_pos = train_pos[features]
y_train_pos = train_pos['final_position']

X_test_pos = test_pos[features]
y_test_pos = test_pos['final_position']

# Train regressor

pos_model = XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    random_state=42
)

pos_model.fit(X_train_pos, y_train_pos)

# Predict

pos_predictions = pos_model.predict(X_test_pos)

# Evaluate

mae = mean_absolute_error(y_test_pos, pos_predictions)

print("Position Model MAE:", mae)

# Save model

joblib.dump(pos_model, 'models/pos_model.pkl')

print("Saved pos_model.pkl")
