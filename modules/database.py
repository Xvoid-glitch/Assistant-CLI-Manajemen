import sqlite3
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Any

class Database:
    def __init__(self, config_dir: Path):
        self.db_path = config_dir / "rizz_data.db"
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Jadwal pelajaran table
        c.execute('''
            CREATE TABLE IF NOT EXISTS jadwal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hari TEXT NOT NULL,
                mata_pelajaran TEXT NOT NULL,
                waktu_mulai TEXT NOT NULL,
                waktu_selesai TEXT NOT NULL,
                ruangan TEXT,
                pengajar TEXT,
                color_code TEXT DEFAULT '#3498db',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Catatan table
        c.execute('''
            CREATE TABLE IF NOT EXISTS catatan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                isi TEXT NOT NULL,
                tags TEXT,
                kategori TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tasks table
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'pending',
                deadline TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Study sessions (for Pomodoro)
        c.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                duration_minutes INTEGER,
                subject TEXT,
                productivity_score INTEGER,
                distractions TEXT
            )
        ''')
        
        # File conversion history
        c.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_file TEXT,
                output_file TEXT,
                conversion_type TEXT,
                file_size_mb REAL,
                duration_seconds REAL,
                converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expense tracker table
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal DATE DEFAULT CURRENT_DATE,
                jumlah REAL NOT NULL,
                kategori TEXT DEFAULT 'Lainnya',
                deskripsi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Budget table
        c.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bulan TEXT NOT NULL,
                budget_bulanan REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clipboard manager table
        c.execute('''
            CREATE TABLE IF NOT EXISTS clipboard_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                is_pinned BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Habits table
        c.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                emoji TEXT DEFAULT '✅',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Habit logs table
        c.execute('''
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                tanggal DATE DEFAULT CURRENT_DATE,
                completed BOOLEAN DEFAULT 1,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        ''')
        
        # Future goals table
        c.execute('''
            CREATE TABLE IF NOT EXISTS future_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                deadline DATE NOT NULL,
                progress INTEGER DEFAULT 0,
                catatan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Goal reflections table
        c.execute('''
            CREATE TABLE IF NOT EXISTS goal_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                pertanyaan TEXT,
                jawaban TEXT,
                tanggal DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (goal_id) REFERENCES future_goals(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        last_id = c.lastrowid
        conn.close()
        return last_id
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def fetch_one(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(query, params)
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None