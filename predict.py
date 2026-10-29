from pathlib import Path
import joblib, pandas as pd
from .train_model import ROOT,FEATURES,train_model
MODEL=ROOT/"models"/"feeder_load_model.joblib"
def predict_feeders(network,hour=18):
    if not MODEL.exists(): train_model()
    model=joblib.load(MODEL)["model"]; rows=[]; names=[]
    for f,v in network.items():
        rows.append([hour,v["R"],v["Y"],v["B"],415.,45.,.95]); names.append(f)
    pred=model.predict(pd.DataFrame(rows,columns=FEATURES))
    return {f:{p:max(0.,float(pred[i][j])) for j,p in enumerate(("R","Y","B"))} for i,f in enumerate(names)}
