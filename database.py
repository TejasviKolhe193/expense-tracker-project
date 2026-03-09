# database.py
# Handles all database operations using SQLite3
# Demonstrates: Database connectivity, CRUD operations, SQL queries

import sqlite3
from models import Expense

DB_NAME = "expenses.db"


class Database:
    """
    Manages the SQLite database connection and all CRUD operations.
    Uses context manager pattern for safe connection handling.
    """

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        """Create and return a database connection."""
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        """Create the expenses table if it doesn't already exist."""
        query = """
            CREATE TABLE IF NOT EXISTS expenses (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                title    TEXT    NOT NULL,
                amount   REAL    NOT NULL,
                category TEXT    NOT NULL,
                date     TEXT    NOT NULL,
                note     TEXT
            );
        """
        with self._connect() as conn:
            conn.execute(query)
            conn.commit()

    # ─────────────────────── CREATE ───────────────────────

    def add_expense(self, expense: Expense) -> int:
        """Insert a new expense and return its auto-generated ID."""
        query = "INSERT INTO expenses (title, amount, category, date, note) VALUES (?, ?, ?, ?, ?)"
        with self._connect() as conn:
            cursor = conn.execute(query, expense.to_tuple())
            conn.commit()
            return cursor.lastrowid

    # ─────────────────────── READ ─────────────────────────

    def get_all_expenses(self) -> list:
        """Fetch all expense records, newest first."""
        query = "SELECT * FROM expenses ORDER BY date DESC, id DESC"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [Expense.from_row(row) for row in rows]

    def get_expenses_by_category(self, category: str) -> list:
        """Fetch all expenses for a specific category."""
        query = "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC"
        with self._connect() as conn:
            rows = conn.execute(query, (category,)).fetchall()
        return [Expense.from_row(row) for row in rows]

    def get_expenses_by_month(self, year: int, month: int) -> list:
        """Fetch expenses for a specific month (e.g., 2024, 5 → May 2024)."""
        month_str = f"{year}-{month:02d}"
        query = "SELECT * FROM expenses WHERE date LIKE ? ORDER BY date"
        with self._connect() as conn:
            rows = conn.execute(query, (f"{month_str}%",)).fetchall()
        return [Expense.from_row(row) for row in rows]

    def search_expenses(self, keyword: str) -> list:
        """Search expenses by title or note (case-insensitive)."""
        query = "SELECT * FROM expenses WHERE title LIKE ? OR note LIKE ? ORDER BY date DESC"
        pattern = f"%{keyword}%"
        with self._connect() as conn:
            rows = conn.execute(query, (pattern, pattern)).fetchall()
        return [Expense.from_row(row) for row in rows]

    # ─────────────────────── UPDATE ───────────────────────

    def update_expense(self, expense: Expense):
        """Update an existing expense by its ID."""
        query = """
            UPDATE expenses
            SET title = ?, amount = ?, category = ?, date = ?, note = ?
            WHERE id = ?
        """
        with self._connect() as conn:
            conn.execute(query, (*expense.to_tuple(), expense.expense_id))
            conn.commit()

    # ─────────────────────── DELETE ───────────────────────

    def delete_expense(self, expense_id: int):
        """Delete a single expense by its ID."""
        query = "DELETE FROM expenses WHERE id = ?"
        with self._connect() as conn:
            conn.execute(query, (expense_id,))
            conn.commit()

    def delete_all(self):
        """Delete every expense record (used for reset)."""
        with self._connect() as conn:
            conn.execute("DELETE FROM expenses")
            conn.commit()

    # ─────────────────────── STATS ────────────────────────

    def get_total(self) -> float:
        """Return the total of all expenses."""
        with self._connect() as conn:
            result = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()
        return result[0] or 0.0

    def get_category_totals(self) -> dict:
        """Return a dict of {category: total_amount}."""
        query = "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return {row[0]: row[1] for row in rows}

    def get_monthly_totals(self) -> dict:
        """Return a dict of {YYYY-MM: total_amount} for trend charts."""
        query = """
            SELECT strftime('%Y-%m', date) AS month, SUM(amount)
            FROM expenses
            GROUP BY month
            ORDER BY month
        """
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return {row[0]: row[1] for row in rows}
