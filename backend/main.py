from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Configuration (You should replace these with your actual Airflow instance details)
AIRFLOW_URL = "http://airflow-url.com/api/v1/dags/"
AIRFLOW_DAG_ID = "dag_id"
AIRFLOW_USERNAME = "username"
AIRFLOW_PASSWORD = "password"


@app.post("/trigger-airflow-pipeline/")
def trigger_airflow_pipeline(file_location: str):
    try:
        # Prepare the request headers with Basic Authentication
        response = requests.post(
            f"{AIRFLOW_URL}{AIRFLOW_DAG_ID}/dagRuns",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            # You can pass configuration for the DAG run here
            json={"conf": {"file_location": file_location}},
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return {"message": "Pipeline triggered successfully."}
        else:
            raise HTTPException(
                status_code=400, detail="Failed to trigger pipeline")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
