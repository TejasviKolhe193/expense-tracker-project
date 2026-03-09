# main.py
# Entry point for the Expense Tracker application
# Run: python main.py

import sys
import os

# Add project folder to path so imports work from any location
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import ExpenseApp


def main():
    app = ExpenseApp()
    app.mainloop()


if __name__ == "__main__":
    main()
