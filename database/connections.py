from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


# Converted to string because Pydantic returns a different object
# Which does not work well with create_engine
POSTGRES_DB_URL = str(settings.postgres_url)
MYSQL_DB_URL = str(settings.mysql_url)

postgres_engine = create_engine(POSTGRES_DB_URL)
PostgresSession = sessionmaker(bind=postgres_engine)

mysql_engine = create_engine(MYSQL_DB_URL)
MysqlSession = sessionmaker(bind=mysql_engine)
