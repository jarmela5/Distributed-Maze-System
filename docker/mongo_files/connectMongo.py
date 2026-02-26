from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
db_name = 'bdlivros'
collection_name = 'livros'
client = MongoClient('localhost', 27017, username='root', password='root', authSource='admin')
#client = MongoClient('localhost:27017,localhost:27018,localhost:27019', replicaSet='ReplicaLivros', username='root', password='root', authSource='admin')
try:
    db = client[db_name]
    collection = db[collection_name]
    num_documentos = collection.count_documents({}) 
    print(f"Número de documentos: {num_documentos}")

except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
finally:
    client.close()
    print("Conexão ao MongoDB fechada.")    
