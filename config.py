# MySQL Database Configuration
# IMPORTANT: Update these credentials with your MySQL connection details
# Default assumes MySQL is running locally with root user

MYSQL_CONFIG = {
    'host': 'localhost',              # Your MySQL host (e.g., 'localhost', '127.0.0.1', or IP address)
    'user': 'root',                   # Your MySQL username (usually 'root' by default)
    'password': 'password',               # Your MySQL password - UPDATE THIS!
    'database': 'be_results_db'       # Database name (B.E Results)
}

# Database name
DB_NAME = 'be_results_db'

# Note: After changing credentials:
# 1. Run: python database.py (to create the database)
# 2. Run: python app.py (to start the Flask app)
# 3. Open http://localhost:5000 in your browser
