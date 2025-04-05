from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from uri_mongodata_login_and_password import mongo_uri
mongo_client =  MongoClient(mongo_uri, server_api=ServerApi('1'))
mongo_db = mongo_client.db
mongo_collections = mongo_db.users

