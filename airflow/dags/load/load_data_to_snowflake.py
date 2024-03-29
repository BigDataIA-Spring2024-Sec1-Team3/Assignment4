from sqlalchemy import create_engine, text
import configparser

def load_data_to_snowflake_func(file_name):
    config = configparser.ConfigParser()
    config.read('configuration.properties')

    user = config['SNOWFLAKE']['User']
    password = config['SNOWFLAKE']['Password']
    account = config['SNOWFLAKE']['Account']
    warehouse = config['SNOWFLAKE']['Warehouse']
    database = config['SNOWFLAKE']['Database']
    schema = config['SNOWFLAKE']['Schema']
    content_table_name = config['SNOWFLAKE']['PDF_CONTENT_TABLE']
    content_stage_name = config['SNOWFLAKE']['PDF_CONTENT_STAGE']
    metadata_table_name = config['SNOWFLAKE']['PDF_METADATA_TABLE']
    metadata_stage_name = config['SNOWFLAKE']['PDF_METADATA_STAGE']
    pdf_data_file_format = config['SNOWFLAKE']['PDF_DATA_FF']

    # Create a connection string
    connection_string = f'snowflake://{user}:{password}@{account}/' \
                            f'?warehouse={warehouse}&database={database}&schema={schema}'
    
    engine = create_engine(connection_string)
                  
    copy_into_query = f"""
    COPY INTO {content_table_name} 
    FROM @{content_stage_name} 
    FILES = ('{file_name}')
    FILE_FORMAT = (FORMAT_NAME = {pdf_data_file_format});
    """
    
    with engine.connect() as connection:
        connection.execute(text(copy_into_query))
    
    print(f"Data loaded from {content_stage_name} to {content_table_name} successfully")
    
    