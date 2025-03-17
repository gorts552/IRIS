import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="celinemysql#1",  # Replace with your actual password
    database="iris_chatbot",  # Replace with your actual database name
    local_infile=True  # This should enable local file loading
)




cursor = conn.cursor()

# Enable local infile for this session (global must be set manually)
cursor.execute("SET SESSION local_infile = 1;")

# Load data from CSV file
csv_file_path = r"C:/ProgramData/MySQL/MySQL Server 8.0/Uploads "  # Replace with your actual file path

query = f"""
LOAD DATA LOCAL INFILE '{csv_file_path}'
INTO TABLE health_info  # Replace with your actual table name
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\r\n'  # Windows line break
IGNORE 1 ROWS;
"""

try:
    cursor.execute(query)
    conn.commit()
    print("🎉 Data successfully loaded into MySQL!")
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

cursor.close()
conn.close()
