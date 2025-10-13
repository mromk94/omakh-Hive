#!/bin/bash

echo "🔧 OMK Hive Database Setup"
echo "=========================="
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed"
    echo "Install MySQL:"
    echo "  macOS: brew install mysql"
    echo "  Ubuntu: sudo apt-get install mysql-server"
    exit 1
fi

echo "✅ MySQL found"
echo ""

# Database credentials
DB_NAME="omk-hive1"
DB_PASSWORD="Successtrain2025@@"

echo "📦 Creating database: $DB_NAME"
echo ""

# Create database
mysql -u root -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database created successfully"
else
    echo "⚠️  Attempting to create database (you may need to enter MySQL root password)"
    mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
fi

echo ""
echo "📦 Installing Python dependencies..."
if [ -d "venv" ]; then
    echo "Using virtual environment..."
    source venv/bin/activate
    pip install pymysql cryptography passlib python-jose bcrypt
elif command -v pip3 &> /dev/null; then
    pip3 install pymysql cryptography passlib python-jose bcrypt
else
    echo "⚠️  pip not found, skipping dependency install"
fi

echo ""
echo "🌱 Initializing database tables and seeding data..."
cd "$(dirname "$0")"

# Try different Python commands
if [ -d "venv" ]; then
    source venv/bin/activate
    python app/database/init_db.py
elif command -v python3 &> /dev/null; then
    python3 app/database/init_db.py
elif command -v python &> /dev/null; then
    python app/database/init_db.py
else
    echo "❌ Python not found"
    exit 1
fi

echo ""
echo "✅ Database setup complete!"
echo ""
echo "📝 Admin Login:"
echo "   Email: king@omakh.io"
echo "   Password: Successtrain2025@@"
echo ""
echo "📝 Demo Users:"
echo "   Email: demo1@omakh.io / demo2@omakh.io"
echo "   Password: demouser1234"
echo ""
