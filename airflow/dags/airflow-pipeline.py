from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from extraction.pdf_extraction import process_pdf_content
from validation.corrections.correction_pdf_content import content_clean_csv_generate
# from validation.corrections.correction_pdf_metadata import metadata_validate_data, metadata_clean_csv_generate
from load.load_data_to_snowflake import load_data_to_snowflake_func
import configparser

dag= DAG(
    dag_id= "trigger_pipeline",
    description='DAG triggered by FastAPI call',
    schedule_interval=None,
)

def extract_data(**kwargs):
    s3_uri = kwargs['dag_run'].conf.get("s3_uri")
    csv_s3_uri = process_pdf_content(s3_uri)
    kwargs['ti'].xcom_push(key='raw_csv', value=csv_s3_uri)
    
def validate_data(**kwargs):
    pulled_value = kwargs['ti'].xcom_pull(dag_id='trigger_pipeline', task_ids='Data_Extraction_task', key='raw_csv')
    file_name = content_clean_csv_generate(pulled_value)
    kwargs['ti'].xcom_push(key='clean_csv', value=file_name)
    
def load_data(**kwargs):
    pulled_value = kwargs['ti'].xcom_pull(dag_id='trigger_pipeline', task_ids='Content_Validation_task', key='clean_csv')
    load_data_to_snowflake_func(pulled_value)

config = configparser.ConfigParser()
config.read('dags/configuration.properties')

file_format_name = config['SNOWFLAKE']['pdf_data_file_format']
content_table_name = config['SNOWFLAKE']['content_table_name']
content_stage_name = config['SNOWFLAKE']['content_stage_name']
metadata_table_name = config['SNOWFLAKE']['metadata_table_name']
metadata_stage_name = config['SNOWFLAKE']['metadata_stage_name']

with dag:
    
    extraction_task = PythonOperator(
        task_id='Data_Extraction_task',
        python_callable=extract_data
    )
    
    content_validation = PythonOperator(
        task_id='Content_Validation_task',
        python_callable=validate_data
    )
    
    load_data_snowflake =PythonOperator(
        task_id='Load_data_snowflake',
        python_callable=load_data
    )

    extraction_task >> content_validation >> load_data_snowflake