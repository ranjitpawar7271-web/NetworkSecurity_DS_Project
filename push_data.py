import os
import json
import sys 

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URL")

import certifi
ca = certifi.where()

import pandas as pd
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


class NetworkDataExtract():
    
    def __init__(self):
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URI, tlsCAFile=ca)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def csv_to_json_converter(self, file_path):
        try:
            df = pd.read_csv(file_path)
            df.reset_index(drop=True, inplace=True)
            json_data = list(json.loads(df.T.to_json()).values())
            return json_data
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_to_mongodb(self, data, database, collection_name):
        try:
            collection = self.mongo_client[database][collection_name]
            collection.insert_many(data)
            return len(data)
        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE = "NetworkSecurity"
    COLLECTION_NAME = "NetworkData"

    networkobject = NetworkDataExtract()

    json_data = networkobject.csv_to_json_converter(file_path=FILE_PATH)

    no_of_records = networkobject.insert_data_to_mongodb(
        data=json_data,
        database=DATABASE,
        collection_name=COLLECTION_NAME
    )

    print(f"{no_of_records} records inserted successfully into MongoDB collection '{COLLECTION_NAME}' in database '{DATABASE}'.")
