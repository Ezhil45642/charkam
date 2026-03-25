import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "cases.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            law TEXT NOT NULL,
            explanation TEXT NOT NULL,
            steps TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_case(query, law, explanation, steps):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    steps_str = "|||".join(steps) # simple serialization
    cursor.execute('''
        INSERT INTO cases (query, law, explanation, steps)
        VALUES (?, ?, ?, ?)
    ''', (query, law, explanation, steps_str))
    conn.commit()
    conn.close()

def get_all_cases():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT query, law, explanation, steps FROM cases ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    cases = []
    for row in rows:
        cases.append({
            "query": row[0],
            "response": {
                "law": row[1],
                "explanation": row[2],
                "steps": row[3].split("|||") if row[3] else []
            }
        })
    return cases
