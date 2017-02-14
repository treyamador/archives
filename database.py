# database interface
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from discography import Discography
from pymongo.errors import PyMongoError
import subprocess


class Database:


    def __init__(self):
        mongod = 'mongod'
        mongo = 'C:\\Program Files\\MongoDB\\Server\\3.2\\bin\\mongo'
        dbpath = '--dbpath'
        datapath = 'C:\\data\\db'
        self.mongod = subprocess.Popen([mongod,dbpath,datapath])

        client = MongoClient('localhost',27017)
        database = client['metal_archives']
        self.db = database['discogs']


    def __del__(self):
        self.terminate()


    def insert(self,discog):
        if isinstance(discog,Discography):
            discog = discog.retrieve()
        try:
            mid = self.db.insert_one(discog)
        except PyMongoError as err:
            print('Database error:\n',err.args)
        else:
            print('Entry',mid,'inserted into database')


    def terminate(self):
        self.mongod.terminate()
        print('Database closed.')

