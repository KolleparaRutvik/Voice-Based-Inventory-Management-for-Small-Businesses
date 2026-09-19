"""DukaanSetu — Database Schema Migration Script.
Connects directly to Supabase PostgreSQL in ap-northeast-1 and executes database/schema.sql.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
load_dotenv()

def apply_schema():
    db_password = os.getenv('DB_PASSWORD') or 'J5iD8tNjdegLJzJe'
    project_ref = "cauvtvhqjvseuyqazpqu"
    region = "ap-northeast-1"
    host = f"aws-0-{region}.pooler.supabase.com"
    user = f"postgres.{project_ref}"

    schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_file):
        print(f"ERROR: Schema file not found at {schema_file}")
        return False

    with open(schema_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    print(f"Connecting to Supabase PostgreSQL at {host}:6543 as {user}...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=6543,
            user=user,
            password=db_password,
            dbname="postgres",
            sslmode="require",
            connect_timeout=15
        )
        conn.autocommit = True
        cur = conn.cursor()
        print("Executing schema.sql on Supabase PostgreSQL...")
        cur.execute(sql)
        print("\n🎉 SUCCESS: All tables, indexes, triggers, and RLS policies created in Supabase!")
        
        # Verify created tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = [r[0] for r in cur.fetchall()]
        print(f"\nCreated {len(tables)} tables in Supabase:")
        for t in tables:
            print(f"  ✓ {t}")

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to execute schema: {e}")
        return False

if __name__ == '__main__':
    apply_schema()
