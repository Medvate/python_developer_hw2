from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base


metadata = MetaData()
# DATABASE = {
#     'drivername': 'postgres',
#     'host': 'localhost',
#     'port': '5433',
#     'username': 'docker',
#     'password': 'docker',
#     'database': 'covid'
# }
#
# engine = create_engine(URL(**DATABASE), echo=True)
conn_url = "postgresql+psycopg2://docker:docker@covid_postgres/covid"
engine = create_engine(conn_url, echo=True)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()
