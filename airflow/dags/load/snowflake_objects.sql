-- using role SYSADMIN to create all objects
USE ROLE SYSADMIN;

-- creating warehouse BIG_DATA_PROJECT_WH
CREATE WAREHOUSE IDENTIFIER('"BIG_DATA_PROJECT_WH"') 
    WAREHOUSE_SIZE = 'X-Small' 
    AUTO_RESUME = true 
    AUTO_SUSPEND = 60 
    ENABLE_QUERY_ACCELERATION = false 
    WAREHOUSE_TYPE = 'STANDARD' 
    MIN_CLUSTER_COUNT = 1 
    MAX_CLUSTER_COUNT = 1 
    SCALING_POLICY = 'STANDARD';

USE WAREHOUSE BIG_DATA_PROJECT_WH;

-- Creating DB for PDF data
CREATE DATABASE AUTOMATED_DATA_DB;

-- Creating schema for PDF data
CREATE SCHEMA AUTOMATED_DATA_SCHEMA;

-- creating table for PDF content
CREATE OR REPLACE TABLE PDF_CONTENT_TABLE (
        title VARCHAR, 
        topic_name VARCHAR, 
        year INT, 
        level VARCHAR, 
        learning_outcome VARCHAR
    );

-- creating table for PDF metadata
CREATE OR REPLACE TABLE PDF_METADATA_TABLE (
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
CREATE OR REPLACE FILE FORMAT PDF_DATA_FF
    TYPE = 'CSV'
    FIELD_DELIMITER = '\t'
    SKIP_HEADER = 1
    SKIP_BLANK_LINES = True
    EMPTY_FIELD_AS_NULL = true
    TRIM_SPACE = True;
    
-- creating external stage for PDF Content connected with S3
CREATE OR REPLACE STAGE PDF_CONTENT_STAGE
  URL = 's3://bigdata-assignment4/Content_CSV/'
  FILE_FORMAT = PDF_DATA_FF
  CREDENTIALS=(AWS_KEY_ID='<your-access-key>' AWS_SECRET_KEY='<your-secret-key>');

-- creating external stage for PDF Metadata connected with S3
CREATE OR REPLACE STAGE PDF_METADATA_STAGE
  URL = 's3://bigdata-assignment4/Metadata_CSV/'
  FILE_FORMAT = PDF_DATA_FF
  CREDENTIALS=(AWS_KEY_ID='<your-access-key>' AWS_SECRET_KEY='<your-secret-key>');