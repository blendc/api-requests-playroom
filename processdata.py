import os
import csv
import json
import uuid
import logging
from io import StringIO
from datetime import datetime

import boto3
import requests
import sqlalchemy as db
from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

S3_BUCKET = os.getenv('S3_BUCKET', 'bucket-name')
S3_KEY_PREFIX = os.getenv('S3_KEY_PREFIX', '/some/path/')
AWS_REGION = os.getenv('AWS_REGION', 'region')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'key-id')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'access-key')

DB_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:password@localhost:5432/yadayadayada')

s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

engine = db.create_engine(DB_URI)
Session = sessionmaker(bind=engine)

metadata = db.MetaData()
data_table = db.Table(
    'data', 
    metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('name', db.String(255), nullable=False),
    db.Column('email', db.String(255), nullable=False, unique=True),
    db.Column('age', db.Integer, nullable=False)
)

metadata.create_all(engine)

def authenticate_user(username, password):
    login_url = os.getenv('LOGIN_URL', 'https://yada.com/api/login')
    credentials = {'username': username, 'password': password}
    
    try:
        response = requests.post(login_url, data=credentials)
        response.raise_for_status()
        
        token = response.json().get('token')
        if not token:
            raise Exception("Authentication token not found in response")
            
        return token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to authenticate user '{username}': {e}")
        raise Exception(f"Login failed: {str(e)}")


def fetch_csv_data(token):
    csv_url = os.getenv('CSV_URL', 'https://yada.com/api/data')
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(csv_url, headers=headers)
        response.raise_for_status()
        return response.text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch CSV data: {e}")
        raise Exception(f"Failed to fetch CSV data: {str(e)}")


def convert_csv_to_json(csv_data):
    try:
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        json_data = [row for row in reader]
        return json_data
        
    except Exception as e:
        logger.error(f"Failed to convert CSV to JSON: {e}")
        raise Exception(f"CSV conversion error: {str(e)}")


def save_to_database(json_data):
    db_session = Session()
    
    try:
        for entry in json_data:
            insert_query = data_table.insert().values(
                name=entry['name'],
                email=entry['email'],
                age=int(entry['age'])
            )
            db_session.execute(insert_query)
            
        db_session.commit()
        logger.info(f"Successfully saved {len(json_data)} records to database")
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Database error: {e}")
        raise Exception(f"Failed to save data to the database: {str(e)}")
        
    finally:
        db_session.close()


def upload_to_s3(json_data):
    try:
        json_string = json.dumps(json_data, indent=2)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{S3_KEY_PREFIX}{uuid.uuid4()}_{timestamp}.json"
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=unique_filename,
            Body=json_string,
            ContentType='application/json'
        )
        
        logger.info(f"Data uploaded to S3: s3://{S3_BUCKET}/{unique_filename}")
        
    except Exception as e:
        logger.error(f"Failed to upload data to S3: {e}")
        raise Exception(f"Failed to upload data to S3: {str(e)}")

@app.route('/process-data', methods=['POST'])
def process_data():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        logger.info(f"Processing data for user: {username}")
        
        token = authenticate_user(username, password)
        csv_data = fetch_csv_data(token)
        json_data = convert_csv_to_json(csv_data)
        save_to_database(json_data)
        upload_to_s3(json_data)
        
        return jsonify({
            "message": "Data processed successfully",
            "records_processed": len(json_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
