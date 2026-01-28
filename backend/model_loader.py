import os 
import mlflow 
import mlflow.pyfunc 

MODEL_NAME = os.getenv("MODEL_NAME", "churn-model") 
MODEL_STAGE = os.getenv("MODEL_STAGE", "Staging") 

def load_model(): 
    tracking_uri = os.environ["MLFLOW_TRACKING_URI"] 
    token = os.environ["MLFLOW_TRACKING_TOKEN"] 
    mlflow.set_tracking_uri(tracking_uri) 
    os.environ["MLFLOW_TRACKING_USERNAME"] = token 
    os.environ["MLFLOW_TRACKING_PASSWORD"] = token 
 
    # MLflow supports stage-based URI like: 
    # models:/<name>/<stage> 
    uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}" 
    return mlflow.pyfunc.load_model(uri)
