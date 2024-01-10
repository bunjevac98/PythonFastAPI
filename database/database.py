from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Format of connection string
# Sqlalchemy_url=""postgresql://postgres:username:password@ipaddress-hostname/PythonFastAPI""

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Ackosi98@localhost/PythonFastAPI"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocla = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency db.close not working
def get_db():
    db = SessionLocla()
    try:
        yield db
    finally:
        db.close()
