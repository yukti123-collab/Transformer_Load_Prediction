# Transformer Load Balancing Prototype

Windows commands (run from this folder):
```bat
py -m venv venv
venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py data\generate_data.py
py -m ai_model.train_model
py -m streamlit run interface\app.py
```
Open http://localhost:8501. Data is synthetic; this is not a real equipment controller.
