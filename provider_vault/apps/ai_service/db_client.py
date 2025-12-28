"""
Database Client for Provider Vault AI Service

Simple helper module to read provider data from PostgreSQL.
Python only READS data - no writes (Elixir CLI handles data management).
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    """Get a database connection."""
    return psycopg2.connect(DATABASE_URL)

def get_provider_by_npi(npi):
    """
    Fetch a single provider by NPI.
    
    Args:
        npi (str): National Provider Identifier
        
    Returns:
        dict: Provider data or None if not found
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    npi,
                    name,
                    specialty,
                    state,
                    city,
                    address,
                    phone,
                    inserted_at,
                    updated_at
                FROM providers
                WHERE npi = %s
            """, (npi,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_providers_by_specialty(specialty, limit=50):
    """
    Fetch providers by specialty.
    
    Args:
        specialty (str): Provider specialty
        limit (int): Maximum number of results
        
    Returns:
        list[dict]: List of provider records
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    npi,
                    name,
                    specialty,
                    state,
                    city,
                    address,
                    phone
                FROM providers
                WHERE specialty = %s
                LIMIT %s
            """, (specialty, limit))
            return cursor.fetchall()
    finally:
        conn.close()

def get_providers_by_state(state, limit=100):
    """
    Fetch providers by state.
    
    Args:
        state (str): Two-letter state code (e.g., 'CA', 'NY')
        limit (int): Maximum number of results
        
    Returns:
        list[dict]: List of provider records
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    npi,
                    name,
                    specialty,
                    state,
                    city
                FROM providers
                WHERE state = %s
                LIMIT %s
            """, (state, limit))
            return cursor.fetchall()
    finally:
        conn.close()

def get_specialty_distribution():
    """
    Get count of providers by specialty.
    
    Returns:
        list[dict]: Specialty counts sorted by frequency
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    specialty,
                    COUNT(*) as provider_count
                FROM providers
                GROUP BY specialty
                ORDER BY provider_count DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()

def get_state_distribution():
    """
    Get count of providers by state.
    
    Returns:
        list[dict]: State counts sorted by frequency
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    state,
                    COUNT(*) as provider_count
                FROM providers
                GROUP BY state
                ORDER BY provider_count DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()

def get_all_specialties():
    """
    Get list of all unique specialties.
    
    Returns:
        list[str]: Sorted list of specialty names
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT specialty
                FROM providers
                ORDER BY specialty
            """)
            return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def test_connection():
    """
    Test database connection and return basic stats.
    
    Returns:
        dict: Database statistics
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT COUNT(*) as total_providers FROM providers")
            total = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(DISTINCT specialty) as specialty_count FROM providers")
            specialties = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(DISTINCT state) as state_count FROM providers")
            states = cursor.fetchone()
            
            return {
                'total_providers': total['total_providers'],
                'total_specialties': specialties['specialty_count'],
                'total_states': states['state_count'],
                'connection_status': 'Connected successfully!'
            }
    finally:
        conn.close()

# Quick test when run directly
if __name__ == "__main__":
    print("Testing database connection...")
    try:
        stats = test_connection()
        print("\n✅ Database Connection Successful!")
        print(f"   Total Providers: {stats['total_providers']}")
        print(f"   Total Specialties: {stats['total_specialties']}")
        print(f"   Total States: {stats['total_states']}")
        
        print("\n📊 Sample Data:")
        specialties = get_all_specialties()[:5]
        print(f"   First 5 Specialties: {', '.join(specialties)}")
        
    except Exception as e:
        print(f"\n❌ Database Connection Failed!")
        print(f"   Error: {e}")
        print("\n   Check your .env file configuration.")