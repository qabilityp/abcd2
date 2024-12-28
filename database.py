import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'example')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('DB_NAME', 'postgres')

print("DB_USER:", DB_USER)
print("DB_PASSWORD:", DB_PASSWORD)
print("DB_HOST:", DB_HOST)
print("DB_NAME:", DB_NAME)


connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}?client_encoding=utf8"
engine = create_engine(connection_string)
print(f"Connection String: {connection_string}")

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine, checkfirst=True)

def shutdown_session():
    db_session.remove()