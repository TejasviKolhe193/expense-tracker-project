# models.py
# Defines the Expense data model using Object-Oriented Programming

from datetime import date

CATEGORIES = ["Food", "Transport", "Shopping", "Entertainment", "Health", "Bills", "Education", "Other"]


class Expense:
    """
    Represents a single expense entry.
    Demonstrates OOP: encapsulation of data and behavior together.
    """

    def __init__(self, title: str, amount: float, category: str, date_str: str, note: str = "", expense_id: int = None):
        self.expense_id = expense_id  # None when not yet saved to DB
        self.title = title
        self.amount = amount
        self.category = category
        self.date = date_str
        self.note = note

    def __str__(self):
        return f"[{self.date}] {self.title} | ₹{self.amount:.2f} | {self.category}"

    def __repr__(self):
        return f"Expense(id={self.expense_id}, title='{self.title}', amount={self.amount})"

    def to_tuple(self):
        """Convert to tuple for SQLite insertion."""
        return (self.title, self.amount, self.category, self.date, self.note)

    @staticmethod
    def from_row(row: tuple):
        """Create an Expense object from a database row."""
        return Expense(
            expense_id=row[0],
            title=row[1],
            amount=row[2],
            category=row[3],
            date_str=row[4],
            note=row[5]
        )

    @staticmethod
    def today():
        """Returns today's date as string."""
        return date.today().strftime("%Y-%m-%d")
