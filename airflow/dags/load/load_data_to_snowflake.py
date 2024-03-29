from sqlalchemy import create_engine, text
import configparser

def load_data_to_snowflake_func(file_name):
    config = configparser.ConfigParser()
    config.read('dags/configuration.properties')

    user = config['SNOWFLAKE']['User']
    password = config['SNOWFLAKE']['Password']
    account = config['SNOWFLAKE']['Account']
    warehouse = config['SNOWFLAKE']['Warehouse']
    database = config['SNOWFLAKE']['Database']
    schema = config['SNOWFLAKE']['Schema']
    content_table_name = config['SNOWFLAKE']['content_table_name']
    content_stage_name = config['SNOWFLAKE']['content_stage_name']
    metadata_table_name = config['SNOWFLAKE']['metadata_table_name']
    metadata_stage_name = config['SNOWFLAKE']['metadata_stage_name']
    pdf_data_file_format = config['SNOWFLAKE']['pdf_data_file_format']

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
    
    