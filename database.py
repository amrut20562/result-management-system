import mysql.connector
from config import MYSQL_CONFIG, DB_NAME

def get_db_connection():
    """Create and return a MySQL database connection"""
    return mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )

def create_database():
    """Create database and tables in MySQL"""
    # Connect to MySQL server without selecting a database
    conn = mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password']
    )
    cursor = conn.cursor()
    
    # Drop existing database if exists
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    print("🗑️ Old database deleted")
    
    # Create new database
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"✅ Database '{DB_NAME}' created!")
    
    cursor.close()
    conn.close()
    
    # Connect to the new database
    conn = mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''
    CREATE TABLE students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        roll_no VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        semester INT DEFAULT 4,
        email VARCHAR(100),
        phone VARCHAR(15)
    )
    ''')
    
    # Subjects Table
    cursor.execute('''
    CREATE TABLE subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_code VARCHAR(20) UNIQUE,
        subject_name VARCHAR(100) NOT NULL,
        credits INT DEFAULT 4
    )
    ''')
    
    # Insert B.E AIDS Semester Subjects
    be_subjects = [
        ('AIDS2401', 'Machine Learning & Algorithms', 4),
        ('AIDS2402', 'Data Engineering & ETL', 4),
        ('AIDS2403', 'Advanced Statistics for AI', 4),
        ('AIDS2404', 'Neural Networks & Deep Learning', 4),
        ('AIDS2405', 'Data Mining & Knowledge Discovery', 4),
        ('AIDS2406', 'Natural Language Processing', 4)
    ]
    
    insert_query = 'INSERT INTO subjects (subject_code, subject_name, credits) VALUES (%s, %s, %s)'
    cursor.executemany(insert_query, be_subjects)
    
    # Marks Table
    cursor.execute('''
    CREATE TABLE marks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        subject_id INT NOT NULL,
        marks INT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Database created with ALL 6 B.E subjects!")
    print("   Subjects added:")
    for code, name, _ in be_subjects:
        print(f"   • {code} - {name}")
    print(f"\n✅ Connection: {MYSQL_CONFIG['host']} / {MYSQL_CONFIG['database']}")

if __name__ == "__main__":
    create_database()