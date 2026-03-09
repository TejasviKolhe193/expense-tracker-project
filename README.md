# 💸 Expense Tracker
**Mini Project | B.Tech CSE – 4th Semester**

---

## 📌 Project Overview
A desktop Expense Tracker application built with Python that allows users to **add, edit, delete, search, and visualize** their daily expenses. Data is persisted using a local SQLite database.

---

## 🛠️ Tools & Technologies

| Component     | Technology         | Reason                                        |
|---------------|--------------------|-----------------------------------------------|
| Language      | Python 3.10+       | Core programming language                     |
| GUI           | Tkinter (built-in) | Simple desktop GUI, no extra setup            |
| Database      | SQLite3 (built-in) | Lightweight relational DB, no server needed   |
| Charts        | Matplotlib         | Data visualization library                    |
| Architecture  | OOP + Modular      | Separation of concerns across multiple files  |

---

## 🗂️ Project Structure

```
expense_tracker/
│
├── main.py        ← Entry point (run this file)
├── gui.py         ← Tkinter GUI: all windows, forms, charts
├── database.py    ← Database class: all CRUD operations (SQLite)
├── models.py      ← Expense class: data model using OOP
├── utils.py       ← Helper functions: validation, formatting
│
├── expenses.db    ← Auto-created SQLite database file
└── README.md      ← This file
```

---

## ⚙️ Setup & Run

### Step 1 – Install Python
Make sure Python 3.10 or above is installed.
```bash
python --version
```

### Step 2 – Install dependencies
Only one external library is needed:
```bash
pip install matplotlib
```
> Tkinter and SQLite3 come pre-installed with Python.

### Step 3 – Run the application
```bash
cd expense_tracker
python main.py
```

---

## 🎯 Features

| Feature             | Description                                          |
|---------------------|------------------------------------------------------|
| ➕ Add Expense       | Add expense with title, amount, category, date, note |
| ✏️ Edit Expense      | Click any row → edit in form → Save Edit             |
| 🗑️ Delete Expense   | Select row → Delete                                  |
| 🔍 Search           | Search by keyword in title or note                   |
| 📂 Category Filter  | Filter expenses by category                          |
| 🥧 Pie Chart        | Spending breakdown by category                       |
| 📈 Monthly Trend    | Line chart showing month-wise spending               |
| 📊 Bar Chart        | Bar chart comparison across categories               |
| 💾 Persistent Data  | All data saved in SQLite, survives app restarts       |

---

## 📚 Concepts Demonstrated

1. **Object-Oriented Programming** – `Expense` class with attributes, `__str__`, `__repr__`, static methods; `Database` class with encapsulated DB logic
2. **SQLite Database** – DDL (CREATE TABLE), DML (INSERT, SELECT, UPDATE, DELETE), aggregate queries (SUM, GROUP BY)
3. **GUI Programming** – Tkinter Frames, Labels, Entry, Combobox, Treeview, Button events, Toplevel windows
4. **Data Visualization** – Pie chart, line chart, bar chart using Matplotlib
5. **Input Validation** – Type checking, range checking, date format validation
6. **Modular Design** – Code split into meaningful modules (models, database, utils, gui)
7. **Error Handling** – try-except blocks for DB operations and data parsing

---

## 🗄️ Database Schema

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT    NOT NULL,
    amount   REAL    NOT NULL,
    category TEXT    NOT NULL,
    date     TEXT    NOT NULL,
    note     TEXT
);
```

---

## 📸 Categories Supported
Food, Transport, Shopping, Entertainment, Health, Bills, Education, Other

---

## 🔮 Possible Future Enhancements
- Export data to CSV/Excel
- Monthly budget limit + alerts
- User login with password hashing
- Deploy as a Flask web app

---

## 👨‍💻 Author
*Your Name Here* | B.Tech CSE | Semester 4
