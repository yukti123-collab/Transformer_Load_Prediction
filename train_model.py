from pathlib import Path
import sys, joblib, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from data.generate_data import generate
FEATURES=["Hour","R_Current","Y_Current","B_Current","Voltage","Temperature","Power_Factor"]
TARGETS=["Next_R","Next_Y","Next_B"]
def train_model():
    path=ROOT/"data"/"feeder_data.csv"
    df=pd.read_csv(path) if path.exists() else generate()
    model=MultiOutputRegressor(RandomForestRegressor(n_estimators=150,random_state=42,min_samples_leaf=2))
    model.fit(df[FEATURES],df[TARGETS]); err=mean_absolute_error(df[TARGETS],model.predict(df[FEATURES]))
    out=ROOT/"models"/"feeder_load_model.joblib"; out.parent.mkdir(exist_ok=True)
    joblib.dump({"model":model,"features":FEATURES},out); print(f"Saved {out}; training MAE={err:.2f} A"); return out
if __name__=="__main__": train_model()
