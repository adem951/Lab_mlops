import os 
from flask import Flask, request, jsonify 
from model_loader import load_model 
 
app = Flask(__name__) 
model = load_model() 
 
@app.get("/health")
def health(): 
    return {"status": "ok", "stage": os.getenv("MODEL_STAGE", "Staging")} 
 
@app.post("/predict")
def predict(): 
    payload = request.get_json(force=True) 
    # Expect "features": [[...10 floats...], [...]] 
    X = payload["features"] 
    preds = model.predict(X) 
    return jsonify({"predictions": preds.tolist()}) 
 
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=8000)
