import sqlite3
from datetime import datetime



class TodoManager:
    def __init__(self):
        self.db='assistant.db'
        self.setup()

    def setup(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS tasks (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           task TEXT NOT NULL,
                           status TEXT DEFAULT 'pending',
                           created_at TEXT DEFAULT CURRENT_TIMESTAMP
                        
                )           
            ''')
        conn.commit()
        conn.close()
        print("Database ready!")

    def add(self,task):
        conn = sqlite3.connect(self.db)   
        cursor=conn.cursor()
        cursor.execute('INSERT INTO tasks (task) VALUES (?)',
                       (task,))
        conn.commit()
        conn.close()
        return f' Task added: {task}'
    
    def get_all(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        tasks = cursor.execute("SELECT id, task, created_at FROM tasks WHERE status = 'pending'").fetchall()
        conn.close()
        return tasks
    
    def complete(self,task_id):
        conn = sqlite3.connect(self.db)
        cursor=conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'completed' WHERE id=?",(task_id,))
        conn.commit()
        conn.close()
        return f' Task completed: {task_id}'
    
    def delete(self,task_id):
        conn = sqlite3.connect(self.db)
        cursor=conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id  =?",(task_id,))
        conn.commit()
        conn.close()
        return f' Task {task_id} deleted!'
    
    def format_list(self):
        tasks=self.get_all()

        if not tasks:
            return'No pending tasks'
        
        result =' Your pending Tasks:\n'
        result += '-' * 30+ '\n'

        for task in tasks:
            result += f'{task[0]}. {task[1]}\n'
        result += '_'*30
        result += f'\nTotal: {len(tasks)} tasks'
        return result
