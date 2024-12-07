import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_NAME = os.getenv("DB_DATABASE")
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
FULL_DATABASE_URL = f"{DATABASE_URL}{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
db_engine = create_engine(FULL_DATABASE_URL)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_database():
    """
    Create the database (if it doesn't exist) and run the SQL script.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`"))
            connection.execute(text(f"USE `{DATABASE_NAME}`"))

            sql_file_path = os.path.join(os.getcwd(), "database.sql")

            if os.path.exists(sql_file_path):
                with open(sql_file_path, "r") as file:
                    sql_statements = file.read()
                    for statement in sql_statements.split(";"):
                        if statement.strip(): 
                            connection.execute(text(statement.strip()))
    except Exception as e:
            print(f"Error initializing database: {e}")