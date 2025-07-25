import sqlite3
from enum import Enum

from config.config import DB_PATH


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    TESTING = "testing"
    TEST_FAILED = "test_failed"
    TEST_SUCCESS = "test_success"


class TaskDB:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS tasks
                            (
                                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                type        TEXT NOT NULL,
                                status      TEXT NOT NULL,
                                value       TEXT,
                                create_time TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
                                update_time TIMESTAMP DEFAULT (DATETIME('now', 'localtime'))
                            )
                            ''')
        self.conn.commit()

    def fetch_pending_tasks(self):
        self.cursor.execute(f'''
                            SELECT *
                            FROM tasks
                            WHERE status = '${Status.PENDING.value}'
                            ORDER BY create_time ASC
                            ''')
        return self.cursor.fetchall()

    def _update_task_status(self, task_id: int, status: str):
        self.cursor.execute('''
                            UPDATE tasks
                            SET status      = ?,
                                update_time = CURRENT_TIMESTAMP
                            WHERE id = ?
                            ''', (status, task_id))
        self.conn.commit()

    def update_task_status_to_done(self, task_id: int):
        self._update_task_status(task_id, Status.DONE.value)

    def update_task_status_to_failed(self, task_id: int):
        self._update_task_status(task_id, Status.FAILED.value)

    def update_task_status_to_running(self, task_id: int):
        self._update_task_status(task_id, Status.RUNNING.value)

    def update_task_status_to_testing(self, task_id: int):
        self._update_task_status(task_id, Status.TESTING.value)

    def update_task_status_to_test_success(self, task_id: int):
        self._update_task_status(task_id, Status.TEST_SUCCESS.value)

    def update_task_status_to_test_failed(self, task_id: int):
        self._update_task_status(task_id, Status.TEST_FAILED.value)

    def add_task(self, task_type: str, value: str) -> int:
        self.cursor.execute('''
                            INSERT INTO tasks (type, status, value)
                            VALUES (?, 'pending', ?)
                            ''', (task_type, value))
        self.conn.commit()
        return self.cursor.lastrowid

    def query_task_by_id(self, task_id: int):
        self.cursor.execute('''
                            SELECT *
                            FROM tasks
                            WHERE id = ?
                            ''', (task_id,))
        return self.cursor.fetchone()
