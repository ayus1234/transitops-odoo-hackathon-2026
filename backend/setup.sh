#!/bin/bash
# Quick setup script for TransitOps backend (Linux/Mac)

echo "=========================================="
echo "TransitOps Backend Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python --version

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your database credentials!"
fi

echo ""
echo "=========================================="
echo "✓ Setup completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Create PostgreSQL database: createdb transitops"
echo "3. Run migrations: alembic upgrade head"
echo "4. Seed data: python seed_data.py"
echo "5. Start server: uvicorn app.main:app --reload"
echo ""
