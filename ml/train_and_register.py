import os 
import json 
import time 
import mlflow 
import mlflow.sklearn 
from sklearn.datasets import make_classification 
from sklearn.linear_model import LogisticRegression 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import accuracy_score 

# MLOps Pipeline - Task 1: Candidate to Staging
MODEL_NAME = os.getenv("MODEL_NAME", "churn-model") 
 
def main(): 
    tracking_uri = os.environ["MLFLOW_TRACKING_URI"] 
    token = os.environ["MLFLOW_TRACKING_TOKEN"] 
    mlflow.set_tracking_uri(tracking_uri) 
    os.environ["MLFLOW_TRACKING_USERNAME"] = token 
    os.environ["MLFLOW_TRACKING_PASSWORD"] = token 
 
    X, y = make_classification(n_samples=2000, n_features=10, random_state=42) 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 
 
    model = LogisticRegression(max_iter=200) 
    model.fit(X_train, y_train) 
    preds = model.predict(X_test) 
    acc = accuracy_score(y_test, preds) 
 
    run_name = f"candidate-{int(time.time())}" 
    with mlflow.start_run(run_name=run_name) as run: 
        mlflow.log_metric("accuracy", float(acc)) 
        mlflow.log_param("model_type", "logreg") 
        mlflow.log_param("data_version", os.getenv("DATA_VERSION", "dvc:unknown")) 
        mlflow.sklearn.log_model(model, artifact_path="model") 
 
        # Register model 
        model_uri = f"runs:/{run.info.run_id}/model" 
        mv = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME) 
 
        out = {"run_id": run.info.run_id, "accuracy": float(acc), "model_version": mv.version} 
        print(json.dumps(out)) 
 
if __name__ == "__main__": 
    main()
