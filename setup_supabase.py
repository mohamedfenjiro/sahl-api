#!/usr/bin/env python3
"""
Supabase Setup Script

This script helps set up your Supabase project with the required tables and security policies.
It reads the SQL commands from supabase_setup.sql and executes them against your Supabase project.

Usage:
    python setup_supabase.py

Environment variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_KEY: Your Supabase service role key (not the anon key)
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables are required.")
    print("Please set them in your .env file or export them in your shell.")
    sys.exit(1)

def read_sql_file(file_path):
    """Read SQL commands from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: SQL file not found at {file_path}")
        sys.exit(1)

def execute_sql(sql):
    """Execute SQL commands against Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Supabase REST API endpoint for SQL queries
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    # Split SQL into individual statements
    statements = sql.split(';')
    
    success_count = 0
    total_statements = len(statements)
    
    for statement in statements:
        statement = statement.strip()
        if not statement:
            continue
            
        data = {"query": statement + ";"}
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Successfully executed SQL statement ({success_count}/{total_statements})")
            else:
                print(f"❌ Failed to execute SQL statement: {response.text}")
        except Exception as e:
            print(f"❌ Error executing SQL: {str(e)}")
    
    return success_count, total_statements

def main():
    """Main function to set up Supabase."""
    print("🚀 Setting up Supabase project...")
    
    # Read SQL commands from file
    sql_file_path = "supabase_setup.sql"
    sql = read_sql_file(sql_file_path)
    
    # Execute SQL commands
    success_count, total_statements = execute_sql(sql)
    
    if success_count == total_statements:
        print(f"✅ Successfully set up Supabase project! ({success_count}/{total_statements} statements executed)")
    else:
        print(f"⚠️ Partially set up Supabase project. ({success_count}/{total_statements} statements executed)")
    
    print("\n📝 Next steps:")
    print("1. Make sure your application is using the correct Supabase URL and API key")
    print("2. Test your application's connection to Supabase")
    print("3. Deploy your application using the instructions in README.md")

if __name__ == "__main__":
    main()