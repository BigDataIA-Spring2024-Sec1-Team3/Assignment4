from sqlalchemy import create_engine, text
import configparser

def load_data_to_snowflake_func(table_name, stage_name, ff_name):
    config = configparser.ConfigParser()
    config.read('configuration.properties')

    user = config['SNOWFLAKE']['User']
    password = config['SNOWFLAKE']['Password']
    account = config['SNOWFLAKE']['Account']
    warehouse = config['SNOWFLAKE']['Warehouse']
    database = config['SNOWFLAKE']['Database']
    schema = config['SNOWFLAKE']['Schema']

    # Create a connection string
    connection_string = f'snowflake://{user}:{password}@{account}/' \
                            f'?warehouse={warehouse}&database={database}&schema={schema}'
    
    engine = create_engine(connection_string)
                  
    copy_into_query = f"""
    COPY INTO {table_name} FROM @{stage_name} FILE_FORMAT = (FORMAT_NAME = {ff_name});
    """
    with engine.connect() as connection:
        connection.execute(text(copy_into_query))
    
    print(f"Data loaded from {stage_name} to {table_name} successfully")
    
    