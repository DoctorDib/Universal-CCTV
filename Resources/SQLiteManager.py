from datetime import datetime

import sqlite3
import threading

class SQLiteManager:
    __table_name: str = "Data/CameraDatabase.db"

    def __init__(self, db_path: str = __table_name):
        self.db_path = db_path
        self.thread_local = threading.local()
        self.get_connection()  # Ensure the connection is created for the current thread
        self.create_table()

    def get_connection(self):
        if not hasattr(self.thread_local, 'connection') or not self.thread_local.connection:
            self.thread_local.connection = sqlite3.connect(self.db_path)
        return self.thread_local.connection

    def create_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS camera_entries (
                uid INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                display_name TEXT,
                is_favourite BOOLEAN,
                is_thumbnail BOOLEAN,
                is_recording BOOLEAN,
                date DATETIME,
                format TEXT
            )
        '''
        with self.get_connection() as connection:
            connection.execute(create_table_query)

    def insert_video(self, file_name: str, data_format: str, display_name: str = None):
        if display_name is None:
            display_name = file_name

        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
            INSERT INTO camera_entries (file_name, display_name, is_favourite, is_thumbnail, is_recording, date, format)
            VALUES (?, ?, 0, 0, 1, ?, ?)
        '''
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(insert_query, (file_name, display_name, current_datetime, data_format))
            uid = cursor.lastrowid
        return uid

    def insert_snapshot(self, file_name: str, is_thumbnail: bool, data_format: str, display_name: str = None):
        if display_name is None:
            display_name = file_name

        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
            INSERT INTO camera_entries (file_name, display_name, is_favourite, is_thumbnail, is_recording, date, format)
            VALUES (?, ?, 0, ?, 0, ?, ?)
        '''
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(insert_query, (file_name, display_name, is_thumbnail, current_datetime, data_format))

    def stop_recording(self, uid: int):
        update_query = '''
            UPDATE camera_entries
            SET is_recording = 0
            WHERE uid = ?
        '''
        with self.get_connection() as connection:
            connection.execute(update_query, (uid,))

    def add_to_favourites(self, uid: int):
        update_query = '''
            UPDATE camera_entries
            SET is_favourite = 1
            WHERE uid = ?
        '''
        with self.get_connection() as connection:
            connection.execute(update_query, (uid,))

    def remove_from_favourites(self, uid: int):
        update_query = '''
            UPDATE camera_entries
            SET is_favourite = 0
            WHERE uid = ?
        '''
        with self.get_connection() as connection:
            connection.execute(update_query, (uid,))

    def delete_entry(self, uid: int):
        delete_query = '''
            DELETE FROM camera_entries
            WHERE uid = ?
        '''
        with self.get_connection() as connection:
            connection.execute(delete_query, (uid,))
    
    def get_entries(self, data_format: str, is_favourite: bool, is_thumbnail: bool = False):
        select_query = '''
            SELECT uid, file_name, display_name, format, is_favourite
            FROM camera_entries
            WHERE format = ? AND is_favourite = ? AND is_thumbnail = ?
        '''
        with self.get_connection() as connection:
            cursor = connection.execute(select_query, (data_format, is_favourite, is_thumbnail))
            result = cursor.fetchall()

        # Create a JSON object
        entries_json = [{"uid": uid, "file_name": file_name, "display_name": display_name, "format": file_format, "is_favourite": is_favourite} for uid, file_name, display_name, file_format, is_favourite in result]
        print(entries_json)
        return entries_json
    
    def get_file_name(self, uid: int) -> str:
        select_query = '''
            SELECT file_name, format
            FROM camera_entries
            WHERE uid = ?
        '''

        with self.get_connection() as connection:
            cursor = connection.execute(select_query, (uid))
            result = cursor.fetchall()

        file_name, format = result
        return f"{file_name}.{format}"

    def close_connection(self):
        self.get_connection().close()
