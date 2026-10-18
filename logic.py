import sqlite3
import hashlib

class PasswordManager:
    def __init__(self, database):
        self.database = database
    def create_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service TEXT,
                login TEXT,
                password_hash TEXT
            )
            ''')
            conn.commit()
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_password(self, user_id, service, login, password):
        password_hash = self._hash_password(password)
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                INSERT INTO passwords (user_id, service, login, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (user_id, service, login, password_hash))
            conn.commit()
        return True
    def get_passwords(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT service, login FROM passwords WHERE user_id = ?
            ''', (user_id,))
            return cur.fetchall()
    def delete_password(self, user_id, service):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''
                DELETE FROM passwords WHERE user_id = ? AND service = ?
            ''', (user_id, service))
            conn.commit()
            return cur.rowcount > 0