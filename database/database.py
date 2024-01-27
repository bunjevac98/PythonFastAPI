from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Format of connection string
# Sqlalchemy_url=""postgresql://postgres:username:password@ipaddress-hostname/PythonFastAPI""
# DATABASE_URL = "postgresql://your-master-username:your-password@your-rds-endpoint:your-port/your-database-name"
# SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.aws_master_username}:{settings.aws_master_password}@{settings.aws_database_endpoint}:{settings.aws_database_port}/{settings.aws_database_name}"

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
