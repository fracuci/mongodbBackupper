import os, sys, datetime, tarfile, os.path
from pymongo import MongoClient
from bson.json_util import dumps


def create_folder_backup(dbname):
    dt = datetime.datetime.now()
    directory = f'backups/bk_{dbname}_{dt.year}-{dt.month}-{dt.day}-T{dt.hour}_{dt.minute}_{dt.second}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def run_backup(mongoUri, dbname):
    client = MongoClient(mongoUri)
    db = client[dbname]
    collections = db.list_collection_names()
    files_to_compress = []
    directory = create_folder_backup(dbname)
    for collection in collections:
        db_collection = db[collection]
        cursor = db_collection.find({})
        filename = f'{directory}/{collection}.json'
        files_to_compress.append(filename)
        with open(filename, 'w') as file:
            file.write('[')
            for document in cursor:
                file.write(dumps(document))
                file.write(',')
            file.write(']')
    tar_file = f'{directory}.tar.gz'
    make_tarfile(tar_file, files_to_compress)


def make_tarfile(output_filename, source_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for filename in source_dir:
        tar.add(filename)
    tar.close()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('[-] Incorrect number of arguments')
        print('python run.py [host] [port] [dbname] [username: optional] [password: optional] ')
        exit()
    else:

        host = None
        port = None
        dbname = None
        username = None
        password = None

        if len(sys.argv) == 4:
            host = sys.argv[1]
            port = sys.argv[2]
            dbname = sys.argv[3]

        else:

            host = sys.argv[1]
            port = sys.argv[2]
            dbname = sys.argv[3]
            username = sys.argv[4]
            password = sys.argv[5]

        if username is None or password is None:

            mongoUri = f'mongodb://{host}:{port}/{dbname}?authSource=admin'

        else:

            mongoUri = f'mongodb://{username}:{password}@{host}:{port}/{dbname}?authSource=admin'

        try:
            run_backup(mongoUri, dbname)
            print('[*] Successfully performed backup')
        except Exception as e:
            print('[-] An unexpected error has occurred')
            print('[-] '+ str(e))
            print('[-] EXIT')