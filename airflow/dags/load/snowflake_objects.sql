-- using role SYSADMIN to create all objects
USE ROLE SYSADMIN;

-- creating warehouse 
CREATE WAREHOUSE IDENTIFIER('"<YOUR_WAREHOUSE_NAME>"') 
    WAREHOUSE_SIZE = 'X-Small' 
    AUTO_RESUME = true 
    AUTO_SUSPEND = 60 
    ENABLE_QUERY_ACCELERATION = false 
    WAREHOUSE_TYPE = 'STANDARD' 
    MIN_CLUSTER_COUNT = 1 
    MAX_CLUSTER_COUNT = 1 
    SCALING_POLICY = 'STANDARD';

USE WAREHOUSE <YOUR_WAREHOUSE_NAME>;

-- Creating DB for PDF data
CREATE DATABASE <YOUR_DATABASE_NAME>;

-- Creating schema for PDF data
CREATE SCHEMA <YOUR_SCHEMA_NAME>;

-- creating table for PDF content
CREATE OR REPLACE TABLE <YOUR_PDF_CONTENT_TABLE> (
        title VARCHAR, 
        topic_name VARCHAR, 
        year INT, 
        level VARCHAR, 
        learning_outcome VARCHAR
    );

-- creating table for PDF metadata
CREATE OR REPLACE TABLE <YOUR_PDF_METADATA_TABLE> (
        text VARCHAR, 
        para INT, 
        bboxes VARCHAR, 
        pages VARCHAR, 
        section_title VARCHAR, 
        section_number VARCHAR, 
        paper_title VARCHAR, 
        file_path VARCHAR
    );

    -- Creating tab separated FF for CSVs
CREATE OR REPLACE FILE FORMAT <YOUR_FILE_FORMAT_NAME>
    TYPE = 'CSV'
    FIELD_DELIMITER = '\t'
    SKIP_HEADER = 1
    SKIP_BLANK_LINES = True
    EMPTY_FIELD_AS_NULL = true
    TRIM_SPACE = True;
    
-- creating external stage for PDF Content connected with S3
CREATE OR REPLACE STAGE <YOUR_CONTENT_STAGE_NAME>
  URL = 's3://<your_bucket_name>/<your-content-csv-folder-path>/'
  FILE_FORMAT = <YOUR_FILE_FORMAT_NAME>
  CREDENTIALS=(AWS_KEY_ID='<your-access-key>' AWS_SECRET_KEY='<your-secret-key>');

-- creating external stage for PDF Metadata connected with S3
CREATE OR REPLACE STAGE <YOUR_METADATA_STAGE_NAME>
  URL = 's3://<your_bucket_name>/<your-metadata-csv-folder-path>/'
  FILE_FORMAT = <YOUR_FILE_FORMAT_NAME>
  CREDENTIALS=(AWS_KEY_ID='<your-access-key>' AWS_SECRET_KEY='<your-secret-key>');