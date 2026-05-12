import datetime
import sqlite3
from pathlib import Path
from .Target import ValidationResult

CREATE_TABLE_STATEMENT = """
CREATE TABLE IF NOT EXISTS generations (
timestamp text not null,
resultname text not null
)
"""

COUNT_ROWS_STATEMENT = """
SELECT COUNT(*) FROM generations
"""

FETCH_PAGE_STATEMENT ="""
SELECT * FROM generations ORDER BY timestamp LIMIT ? OFFSET ?
"""

FETCH_TIMESTAMP_STATEMENT = """
SELECT resultname FROM generations WHERE generations.timestamp == ?
"""

class Persistor:

    """Path to directory where used prompts and responses get saved."""
    persistance_directory: Path
    
    def __init__(self, persistance_directory: Path):
        self.persistance_directory = persistance_directory
        self.persistance_directory.mkdir(parents = True, exist_ok = True)
        self.connection = sqlite3.connect(persistance_directory / 'org.db', check_same_thread = False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(CREATE_TABLE_STATEMENT)
        self.connection.commit()

    def _build_save_path(self, validation_result_name: str, key: str) -> Path:
        return self.persistance_directory / f'{validation_result_name}' / f'{key}.txt'

    def persist(self, validation_result: ValidationResult, prompt: str, raw_output: str, formatted_output: str):
        cursor = self.connection.cursor()
        key: str = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M:%S-%f")
        save_path = self._build_save_path(validation_result.name, key)
        save_path.parent.mkdir(parents = True, exist_ok = True)
        with save_path.open('w') as f:
            f.write('# Prompt used:\n')
            f.write(prompt)
            f.write('\n# Model Output:\n')
            f.write(raw_output)
            f.write('\n# Processed Output:\n')
            f.write(formatted_output)
        cursor.execute("INSERT INTO generations VALUES(?, ?)", (key, validation_result.name))
        self.connection.commit()

    def fetch_single(self, timestamp) -> str | None:
        cursor = self.connection.cursor()
        res = cursor.execute(FETCH_TIMESTAMP_STATEMENT, [timestamp]).fetchone()
        if res is None:
            return None
        validation_result_name = res[0]
        filepath = self._build_save_path(validation_result_name, timestamp)
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except:
            return None


    def fetch_list(self, size: int, page: int):
        cursor = self.connection.cursor()
        res = cursor.execute(FETCH_PAGE_STATEMENT, (size, page * size)).fetchall()
        number_of_pages = int(cursor.execute(COUNT_ROWS_STATEMENT).fetchone()[0] / size)
        return res, number_of_pages
