#!/bin/bash
set -e

# Run security framework seeding
echo "🌱 Seeding security frameworks..."
python scripts/seed_security_frameworks.py

# Start the application
echo "🚀 Starting Cloud Cleaner API..."
python main.py
