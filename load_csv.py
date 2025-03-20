import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text

# Database credentials
DB_USER = "iris_chatbot_user"
DB_PASSWORD = "rWy6A23qAb988nQxwMSTl8gPsjzRSUO3"
DB_HOST = "dpg-cvd8igl2ng1s73drfbd0-a"
DB_PORT = "5432"  # Change if necessary
DB_NAME = "iris_chatbot"
table_name = "health_information"
csv_file_path = r"C:\\Users\\BlvckMoon\\Documents\\GitHub\\IRIS\\health_info.csv" # Replace
CHUNKSIZE = 1000  # Adjust based on available system memory


engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
connection = engine.connect()
metadata = MetaData()

# Table Structure
health_information = Table(
    table_name, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('question', String(500)),
    Column('answer', Text)
)

# Create table if it does not exist
metadata.create_all(engine)

# Read and load CSV in chunks
for chunk in pd.read_csv(csv_file_path, chunksize=CHUNKSIZE):
    chunk.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f'Inserted {len(chunk)} rows...')

print("🎉 Data successfully loaded into PostgreSQL!")
connection.close()