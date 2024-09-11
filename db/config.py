import logging

DB_CONNECTION = "dbname='postgres' user='postgres' password='1' host='localhost' port='5432'"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)