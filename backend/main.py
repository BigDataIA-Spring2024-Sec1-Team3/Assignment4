from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import boto3
from pydantic import BaseModel
from botocore.exceptions import NoCredentialsError, ClientError
import configparser
import jwt
from passlib.context import CryptContext
import datetime
import random
from pymongo import MongoClient
from sqlalchemy import create_engine, text
import requests

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"

app = FastAPI()

config = configparser.RawConfigParser()
config.read('./configuration.properties')

client = MongoClient(config['MONGODB']['MONGODB_URL'])
db = client[config['MONGODB']["DATABASE_NAME"]]
collection = db[config['MONGODB']["COLLECTION_USER"]]

# Password hashing settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

AIRFLOW_URL = config['AIRFLOW']['AIRFLOW_URL']
AIRFLOW_DAG_ID = config['AIRFLOW']['AIRFLOW_DAG_ID']
AIRFLOW_USERNAME = config['AIRFLOW']['AIRFLOW_USERNAME']
AIRFLOW_PASSWORD = config['AIRFLOW']['AIRFLOW_PASSWORD']

user = config['SNOWFLAKE']['User']
password = config['SNOWFLAKE']['Password']
account = config['SNOWFLAKE']['Account']
warehouse = config['SNOWFLAKE']['Warehouse']
database = config['SNOWFLAKE']['Database']
schema = config['SNOWFLAKE']['Schema']

# Create a connection string
connection_string = f'snowflake://{user}:{password}@{account}/' \
                        f'?warehouse={warehouse}&database={database}&schema={schema}'

access_key = config['AWS']['access_key']
secret_key = config['AWS']['secret_key']
bucket_name = config['s3-bucket']['bucket']

# Establish s3 connection
def aws_s3_connection():
    try:
        s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        return s3_client, bucket_name
    except Exception as e:
        print("Exception in aws_s3_connection func: ",e)
        print('S3 Connection Failed')


# User model
class User(BaseModel):
    userid: int
    username: str
    password: str
    email: str

# Function to authenticate user
def authenticate_user(username: str, password: str):
    user = collection.find_one({"username": username })
    # Verify the plain password with the hash password from db
    if not user or not pwd_context.verify(password, user["password"]):
        return False
    return user

# Function to create access token
def create_access_token(username: str):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expiration_time}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = collection.find_one({"username": username })
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
    
# Route to handle user signup
@app.post("/signup")
async def user_signup(user: User):
    if not user:
        return False
    
    user_data = user.dict()
    existing_user = collection.find_one({"username": user_data["username"]})
    if existing_user:
        # return {"error": "User already exists", "message": f"User with username '{user_data['username']}' already exists"}, 400
        raise HTTPException(status_code=400, detail="User already exists") 

    # Hash the password
    user_data["password"] = pwd_context.hash(user_data["password"]);
    result = collection.insert_one(user_data)
    
    if result.inserted_id:
        return {
                "username": user_data["username"],
                "email":user_data["email"],
                "userid":user_data["userid"]
            }
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    
# Route to generate access token after login
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(form_data.username)
    if access_token:
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        return{"message": "Failed"}

# # Function to check if file exists in S3 bucket
def check_file_exists(s3, bucket_name, file_name):
    try:
        s3.head_object(Bucket=bucket_name, Key=file_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise


# Function to upload file to S3
def upload_to_s3(file, s3, bucket_name, file_name):
    if check_file_exists(s3, bucket_name, file_name):
        return False, "File already exists in S3 bucket"
    else:
        try:
            file_contents = file.read()

            # Check if the file is empty
            if not file_contents:
                return False, "Empty file provided"
            
            # Upload the file contents to S3
            s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_contents)
            # s3.upload_fileobj(file, bucket_name, file_name)
            return True, "File uploaded successfully"
        except FileNotFoundError:
            return False, "File not found"
        except NoCredentialsError:
            return False, "Credentials not found"

def mapUserAndFile(user, file_name):
    try:
        collection = db[config['MONGODB']["COLLECTION_USER_FILE"]]
        user_file_data = {"userid": user["userid"], "username": user["username"], "file_name": file_name}
        collection.insert_one(user_file_data)
        return True  
    except Exception as e:
        print(f"An error occurred while mapping user and file: {e}")
        return False  

# FastAPI endpoint to handle file upload
@app.post("/upload/")
async def upload_file_to_s3(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        s3, bucket_name = aws_s3_connection()
        file_name = f"PDF_Files/{file.filename}"
        success, message = upload_to_s3(file.file, s3, bucket_name, file_name)
        s3_file_url="s3://" + bucket_name + "/" + file_name
        if success:
            if(mapUserAndFile(current_user, file.filename)):
                return {"message": message, "file_location": s3_file_url}
        else:
            return {"error": message}
    except Exception as e:
        return {"error": str(e)}
    finally:
        file.file.close()


# Function to trigger the Airflow pipeline 
@app.post("/trigger-airflow-pipeline/")
async def trigger_airflow_pipeline(file_location: str, current_user: User = Depends(get_current_user)):
    try:
        rand1 = random.randint(1,1000)
        rand2 = random.randint(1,1000)
        dag_run_id = str("id_run_" +str(rand1)+str(rand2))
        response = requests.post(
            f"{AIRFLOW_URL}/api/v1/dags/{AIRFLOW_DAG_ID}/dagRuns",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            json={"conf": {"s3_uri": file_location}, "dag_run_id": dag_run_id },
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return {"message": "Pipeline triggered successfully."}
        else:
            raise HTTPException(
                status_code=400, detail="Failed to trigger pipeline")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Define API endpoint to execute SQL queries
@app.post("/execute/")
def execute_query(query: str, current_user: User = Depends(get_current_user)):
    try:
        # Create an engine for Snowflake Connection
        engine = create_engine(connection_string)
        print("Engine created for snowflake sqlalchemy")

        with engine.connect() as conn:
            # Execute the SQL query
            result = conn.execute(query)

            # Fetch all rows from the result
            rows = result.fetchall()
            return {"result": rows}
        
    except Exception as e:
        # Return error message if query execution fails
        raise HTTPException(status_code=500, detail=str(e))