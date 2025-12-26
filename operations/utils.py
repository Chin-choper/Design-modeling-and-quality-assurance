from pymongo import MongoClient

def get_db_handle():
    client = MongoClient('localhost', 27017)
    db = client['ZaporizhzhiaTradeDB']
    db = client['ZaporizhzhiaTradeDB']
    return db, client

def get_collection_handle():
    db, client = get_db_handle()
    return db['trade_operations']
