from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Format of connection string
# Sqlalchemy_url=""postgresql://postgres:username:password@ipaddress-hostname/PythonFastAPI""

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

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


"""
while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="PythonFastAPI",
            user="postgres",
            password="Ackosi98",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("WE CONNECTED")
        break
    except Exception as error:
        print("WE FAILED")
        print("error was:", error)
        time.sleep(3)
"""
