from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor

from app.core import config

@contextmanager
def pg_conn():
    conn = psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
        dbname=config.PG_DBNAME,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_demand_forecast(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the most recent demand forecast for a specific item (categorylv5).
    Returns a single record with forecast details, or None if not found.
    """
    sql = """
        SELECT 
            forecast_date,
            categorylv5,
            demand_forecast
        FROM taokae_internal_data.demand_forecast
        WHERE categorylv5 = %s
        ORDER BY forecast_date DESC
        LIMIT 1
    """
    
    with pg_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (item_name,))
            row = cur.fetchone()
            return dict(row) if row else None

def get_forecast_for_item(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Alias/Wrapper for get_demand_forecast to match user intent of using selected_item
    as query input.
    """
    return get_demand_forecast(item_name)

if __name__ == "__main__":
    # Test block
    try:
        print("Testing DB connection...")
        # Try to connect without querying first to safe check
        with pg_conn() as conn:
            print("Connection successful!")
            
        # Example query (User can change the item name to test)
        item = "กระติกน้ำร้อน"
        print(f"Querying for item: {item}")
        result = get_demand_forecast(item)
        if result:
            print(f"Found record: {result}")
        else:
            print("No record found.")
            
    except Exception as e:
        print(f"DB Error: {e}")
