import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text


# Database credentials
DB_USER = "iris_chatbot_user"
DB_PASSWORD = "rWy6A23qAb988nQxwMSTl8gPsjzRSUO3"
DB_HOST = "dpg-cvd8igl2ng1s73drfbd0-a.oregon-postgres.render.com"
DB_PORT = "5432"  # Change if necessary
DB_NAME = "iris_chatbot"
table_name = "health_info"
csv_file_path = r"C:\\Users\\Celine\\Documents" # Replace
CHUNKSIZE = 1000  # Adjust based on available system memory


engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
connection = engine.connect()
metadata = MetaData()

# Table Structure
health_info = Table(
    table_name, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('question', String(500), nullable=False),
    Column('answer', Text, nullable=False),
)
# Create table if it does not exist
metadata.create_all(engine)

# Read and load CSV in chunks
for chunk in pd.read_csv(csv_file_path, chunksize=CHUNKSIZE):
    chunk.dropna(inplace=True)  # Drop rows with any NULL values
    if not chunk.empty:  # Check if the chunk still has data
        chunk.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f'Inserted {len(chunk)} rows...')
    else:
        print("Skipped empty chunk after dropping NULL rows.")

print("🎉 Data successfully loaded into PostgreSQL!")
connection.close()