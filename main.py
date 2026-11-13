import sqlite3
from datetime import datetime, timedelta

# Function to initialize the database and create the listings table
def initialize_db(db_name=":memory:"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the 'listings' table with freshness-focused columns
    # 'created_at': When the listing was first added.
    # 'updated_at': When the listing was last modified (key for recency).
    # 'is_active': Boolean (0 or 1) indicating if the listing is currently available.
    # 'published_until': An explicit expiration date for the listing.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            published_until TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

# Function to add sample data
def add_sample_data(conn):
    cursor = conn.cursor()
    now = datetime.now()

    listings_data = [
        # 1. Fresh, active, recently updated listing (should appear first)
        ("Modern Daire", "Şehir merkezinde 3+1 lüks daire.", 1500000.0,
         (now - timedelta(days=5)).isoformat(), (now - timedelta(hours=1)).isoformat(), 1, (now + timedelta(days=30)).isoformat()),
        # 2. Older, active listing, but still valid (should appear, but lower priority than #1 and #6)
        ("Geniş Villa", "Deniz manzaralı 5+2 villa.", 3200000.0,
         (now - timedelta(days=60)).isoformat(), (now - timedelta(days=10)).isoformat(), 1, (now + timedelta(days=90)).isoformat()),
        # 3. Active listing, but published_until has passed (should NOT appear due to expiration)
        ("Kiralık Ofis", "İş merkezinde uygun fiyatlı ofis.", 5000.0,
         (now - timedelta(days=20)).isoformat(), (now - timedelta(days=5)).isoformat(), 1, (now - timedelta(days=1)).isoformat()),
        # 4. Inactive listing (is_active = 0) (should NOT appear)
        ("Satılık Arsa", "Yatırıma uygun imarlı arsa.", 800000.0,
         (now - timedelta(days=90)).isoformat(), (now - timedelta(days=30)).isoformat(), 0, (now + timedelta(days=180)).isoformat()),
        # 5. Very recent, but marked inactive (should NOT appear due to is_active=0)
        ("Yeni Daire", "Sıfır 2+1 daire.", 950000.0,
         (now - timedelta(hours=2)).isoformat(), (now - timedelta(hours=1)).isoformat(), 0, (now + timedelta(days=60)).isoformat()),
        # 6. Another fresh, active listing, updated slightly earlier than #1 (should appear second)
        ("Merkezi Konumda Dükkan", "İşlek caddede kiralık dükkan.", 12000.0,
         (now - timedelta(days=10)).isoformat(), (now - timedelta(hours=3)).isoformat(), 1, (now + timedelta(days=45)).isoformat()),
    ]

    cursor.executemany('''
        INSERT INTO listings (title, description, price, created_at, updated_at, is_active, published_until)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', listings_data)
    conn.commit()

# Function to retrieve "fresh" listings
def get_fresh_listings(conn):
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()

    # The core "freshness-first" query:
    # 1. Filter by 'is_active = 1' (listing is currently available).
    # 2. Filter by 'published_until > ?' (listing has not expired).
    # 3. Order by 'updated_at DESC' (prioritize most recently updated listings).
    cursor.execute('''
        SELECT id, title, description, price, updated_at
        FROM listings
        WHERE is_active = 1 AND published_until > ?
        ORDER BY updated_at DESC
    ''', (now_iso,)) # Pass current time for comparison

    return cursor.fetchall()

def main():
    # Initialize an in-memory SQLite database for demonstration
    conn = initialize_db()
    print("Database initialized and 'listings' table created.")

    # Add sample real estate listing data
    add_sample_data(conn)
    print("Sample data added.")

    print("\n--- Retrieving Fresh Listings ---")
    fresh_listings = get_fresh_listings(conn)

    if fresh_listings:
        for listing in fresh_listings:
            print(f"ID: {listing[0]}, Title: {listing[1]}, Price: {listing[3]:,.2f} TL, Last Updated: {listing[4]}")
    else:
        print("No fresh listings found.")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
