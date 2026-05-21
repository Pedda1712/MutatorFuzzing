import datetime
import sqlite3
from pathlib import Path
from .Target import ValidationResult

CREATE_GENERATIONS_TABLE_STATEMENT = """
CREATE TABLE IF NOT EXISTS generations (
timestamp text not null,
resultname text not null
)
"""

CREATE_STATUS_COUNTS_TABLE_STATEMENT = """
CREATE TABLE IF NOT EXISTS status_counts (
name text not null,
value int not null
)
"""

CREATE_COVERAGE_HISTORY_TABLE_STATEMENT = """
CREATE TABLE IF NOT EXISTS coverage_history (
epoch int not null,
relative float not null,
absolute int not null
)
"""

CREATE_RESUMMARIZATION_HISTORY_STATEMENT = """
CREATE TABLE IF NOT EXISTS resummarization (
epoch int not null
)
"""

INSERT_VALIDATION_RESULT_STATEMENT = """
INSERT INTO generations VALUES(?, ?)
"""

INSERT_COVERAGE_STATEMENT = """
INSERT INTO coverage_history VALUES(?, ?, ?)
"""

INSERT_RESUMMARIZATION_STATEMENT = """
INSERT INTO resummarization VALUES(?)
"""

INITIALIZE_STATUS_COUNT_STATEMENT = """
INSERT INTO status_counts (name, value) VALUES (?, ?)
"""

UPDATE_STATUS_COUNT_STATEMENT = """
UPDATE status_counts SET value = ? WHERE name == ?
"""

GET_STATUS_COUNT_STATEMENT = """
SELECT value FROM status_counts WHERE status_counts.name == ?
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

FETCH_COVERAGE_STATEMENT = """
SELECT relative, absolute FROM coverage_history ORDER BY coverage_history.epoch ASC
"""

FETCH_RESUMMARIZATION_STATEMENT = """
SELECT epoch FROM resummarization ORDER BY resummarization.epoch ASC
"""

FETCH_VALIDATION_RESULT_REPORT_STATEMENT = """
SELECT resultname, COUNT(*) FROM generations GROUP BY generations.resultname
"""

class Persistor:

    """Path to directory where used prompts and responses get saved."""
    persistance_directory: Path
    
    def __init__(self, persistance_directory: Path):
        self.persistance_directory = persistance_directory
        self.persistance_directory.mkdir(parents = True, exist_ok = True)
        self.connection = sqlite3.connect(persistance_directory / 'org.db', check_same_thread = False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(CREATE_GENERATIONS_TABLE_STATEMENT)
        self.cursor.execute(CREATE_STATUS_COUNTS_TABLE_STATEMENT)
        self.cursor.execute(CREATE_COVERAGE_HISTORY_TABLE_STATEMENT)
        self.cursor.execute(CREATE_RESUMMARIZATION_HISTORY_STATEMENT)
        self.connection.commit()

    def _build_save_path(self, validation_result_name: str, key: str) -> Path:
        return self.persistance_directory / f'{validation_result_name}' / f'{key}.txt'

    def validity_report(self):
        cursor = self.connection.cursor()
        res = cursor.execute(FETCH_VALIDATION_RESULT_REPORT_STATEMENT).fetchall()
        return res
    
    def get_coverage_history(self):
        cursor = self.connection.cursor()
        res = cursor.execute(FETCH_COVERAGE_STATEMENT).fetchall()
        return res

    def submit_resummarization(self):
        epoch = self.get_epoch()
        cursor = self.connection.cursor()
        cursor.execute(INSERT_RESUMMARIZATION_STATEMENT, (epoch,))
        self.connection.commit()

    def get_resummarization(self):
        cursor = self.connection.cursor()
        res = cursor.execute(FETCH_RESUMMARIZATION_STATEMENT).fetchall()
        if res is None:
            return []
        return res
        
    def submit_coverage(self, relative, absolute):
        epoch = self.get_epoch()
        cursor = self.connection.cursor()
        cursor.execute(INSERT_COVERAGE_STATEMENT, (epoch, relative, absolute))
        self.connection.commit()

    def get_epoch(self):
        cursor = self.connection.cursor()
        res = cursor.execute(GET_STATUS_COUNT_STATEMENT, ('epoch',)).fetchone()
        if res is None:
            cursor.execute(INITIALIZE_STATUS_COUNT_STATEMENT, ('epoch', 0))
            self.connection.commit()
            return 0
        return res[0]

    def bump_epoch(self):
        epoch = self.get_epoch()
        cursor = self.connection.cursor()
        cursor.execute(UPDATE_STATUS_COUNT_STATEMENT, (epoch+1, 'epoch'))
        self.connection.commit()

    def persist(self, validation_result: ValidationResult, prompt: str, raw_output: str, formatted_output: str):
        cursor = self.connection.cursor()
        key: str = datetime.datetime.now().strftime("%Y-%m-%d--%H:%M:%S-%f")
        save_path = self._build_save_path(validation_result.name, key)
        save_path.parent.mkdir(parents = True, exist_ok = True)
        with save_path.open('w') as f:
            f.write('# Prompt used:\n')
            f.write(prompt)
            f.write('\n# Model Output:\n')
            f.write(raw_output)
            f.write('\n# Processed Output:\n')
            f.write(formatted_output)
        cursor.execute(INSERT_VALIDATION_RESULT_STATEMENT, (key, validation_result.name))
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
