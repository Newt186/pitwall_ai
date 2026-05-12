import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    confusion_matrix,
    mean_absolute_error
)

df = pd.read_csv('data/processed/features.csv')
df = df.dropna()

train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

features = [
    'LapNumber',
    'TyreLife',
    'Compound',
    'deg_rate',
    'gap_ahead',
    'undercut_risk',
    'Position'
]

X_train = train_df[features]
y_train = train_df['pit_next_lap']
X_test = test_df[features]
y_test = test_df['pit_next_lap']

ratio = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
print("Class imbalance ratio:", ratio)

pit_model = XGBClassifier(
    objective='binary:logistic',
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    scale_pos_weight=ratio,
    random_state=42
)

pit_model.fit(X_train, y_train)
predictions = pit_model.predict(X_test)

print(classification_report(y_test, predictions))
print("Precision:", precision_score(y_test, predictions))
print("Recall:", recall_score(y_test, predictions))
print(confusion_matrix(y_test, predictions))

joblib.dump(pit_model, 'models/pit_model.pkl')
print("Saved pit_model.pkl")

position_df = df[df['LapNumber'] > 20].copy()

position_df['final_position'] = (
    position_df.groupby([
        'Year',
        'EventName',
        'Driver'
    ])['Position']
    .transform('last')
)

train_pos, test_pos = train_test_split(position_df, test_size=0.2, random_state=42)

X_train_pos = train_pos[features]
y_train_pos = train_pos['final_position']
X_test_pos = test_pos[features]
y_test_pos = test_pos['final_position']

pos_model = XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    random_state=42
)

pos_model.fit(X_train_pos, y_train_pos)
pos_predictions = pos_model.predict(X_test_pos)

mae = mean_absolute_error(y_test_pos, pos_predictions)
print("Position Model MAE:", mae)

joblib.dump(pos_model, 'models/pos_model.pkl')
print("Saved pos_model.pkl")
