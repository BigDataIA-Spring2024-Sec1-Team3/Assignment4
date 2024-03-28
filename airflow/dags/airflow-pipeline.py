from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
# from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from extraction.pdf_extraction import pdf_to_xml_using_grobid, xml_data_to_csv
from validation.corrections.correction_pdf_content import content_validate_data, content_clean_csv_generate
from validation.corrections.correction_pdf_metadata import metadata_validate_data, metadata_clean_csv_generate
from load.load_data_to_snowflake import load_data_to_snowflake_func
import configparser

dag= DAG(
    dag_id= "trigger_pipeline",
    description='DAG triggered by FastAPI call',
    schedule_interval=None,
)

config = configparser.ConfigParser()
config.read('configuration.properties')

file_format_name = config['SNOWFLAKE']['file_format_name']
content_table_name = config['SNOWFLAKE']['content_table_name']
content_stage_name = config['SNOWFLAKE']['content_stage_name']
metadata_table_name = config['SNOWFLAKE']['metadata_table_name']
metadata_stage_name = config['SNOWFLAKE']['metadata_stage_name']

with dag:
    
    extraction_task = PythonOperator(
        task_id='Data_Extraction_task',
        python_callable=pdf_to_xml_using_grobid
    )
    
    content_validation = PythonOperator(
        task_id='Content_Validation_task',
        python_callable=content_validate_data
    )
    
    content_clean_csv =PythonOperator(
        task_id='content_csv_generation_task',
        python_callable=content_clean_csv_generate
    )
    
    metadata_validation = PythonOperator(
        task_id='metadata_Validation_task',
        python_callable=metadata_validate_data
    )
    
    metadata_clean_csv =PythonOperator(
        task_id='metadata_csv_generation_task',
        python_callable=metadata_clean_csv_generate
    )
    
    snowflake_data_load_content = PythonOperator(
        task_id='snowflake_load_content_task',
        python_callable=load_data_to_snowflake_func(content_table_name, content_stage_name,  file_format_name)
    )
    
    snowflake_data_load_metadata = PythonOperator(
        task_id='snowflake_load_metadata_task',
        python_callable=load_data_to_snowflake_func('metadata_table_name','metadata_stage_name','file_format_name')
    )

    extraction_task >> content_validation >> content_clean_csv >> metadata_validation >> metadata_clean_csv >> snowflake_data_load_content >> snowflake_data_load_metadata