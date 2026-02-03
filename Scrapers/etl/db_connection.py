import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kpkr@153",
        database="offerzone_project"
    )
