# gui.py
# Main GUI file using Tkinter
# Features: Add/Edit/Delete expenses, View list, Filter, Charts, Search

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database import Database
from models import Expense, CATEGORIES
from utils import (
    validate_amount, validate_date, validate_title,
    format_currency, format_month_label, get_current_year_month
)

# ─────────────────────── Color Palette ───────────────────────
BG        = "#1e1e2e"
PANEL     = "#2a2a3d"
ACCENT    = "#7c3aed"
ACCENT_LT = "#a78bfa"
SUCCESS   = "#10b981"
DANGER    = "#ef4444"
TEXT      = "#e2e8f0"
SUBTEXT   = "#94a3b8"
ENTRY_BG  = "#16213e"


class ExpenseApp(tk.Tk):
    """
    Main application window.
    Inherits from tk.Tk — root window itself is the app.
    """

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.selected_id = None   # Tracks which expense is selected for edit/delete

        self.title("💸 Expense Tracker")
        self.geometry("1100x680")
        self.configure(bg=BG)
        self.resizable(True, True)

        self._build_ui()
        self._load_table()

    # ═══════════════════════ UI BUILDING ═══════════════════════

    def _build_ui(self):
        """Build all UI sections."""
        self._build_header()
        self._build_main_area()
        self._build_status_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=ACCENT, height=56)
        header.pack(fill=tk.X)
        tk.Label(header, text="💸  Expense Tracker", font=("Segoe UI", 18, "bold"),
                 bg=ACCENT, fg="white").pack(side=tk.LEFT, padx=20, pady=12)

        # Summary labels on the right
        self.total_label = tk.Label(header, text="Total: ₹0.00",
                                    font=("Segoe UI", 12), bg=ACCENT, fg="white")
        self.total_label.pack(side=tk.RIGHT, padx=20)

    def _build_main_area(self):
        main = tk.Frame(self, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Left: Form + Filters | Right: Table + Charts
        left = tk.Frame(main, bg=PANEL, width=320, bd=0)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)

        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_form(left)
        self._build_filter_section(left)
        self._build_table(right)
        self._build_chart_buttons(right)

    def _build_form(self, parent):
        """Add/Edit expense form."""
        frm = tk.LabelFrame(parent, text=" ✏️  Add / Edit Expense ", font=("Segoe UI", 10, "bold"),
                            bg=PANEL, fg=ACCENT_LT, bd=1, relief=tk.GROOVE)
        frm.pack(fill=tk.X, padx=10, pady=(10, 5))

        def lbl(text): return tk.Label(frm, text=text, bg=PANEL, fg=SUBTEXT,
                                       font=("Segoe UI", 9), anchor="w")
        def entry(): return tk.Entry(frm, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                                    font=("Segoe UI", 10), relief=tk.FLAT, bd=4)

        lbl("Title *").pack(fill=tk.X, padx=10, pady=(8, 0))
        self.e_title = entry(); self.e_title.pack(fill=tk.X, padx=10, pady=(2, 6))

        lbl("Amount (₹) *").pack(fill=tk.X, padx=10)
        self.e_amount = entry(); self.e_amount.pack(fill=tk.X, padx=10, pady=(2, 6))

        lbl("Category *").pack(fill=tk.X, padx=10)
        self.e_cat = ttk.Combobox(frm, values=CATEGORIES, state="readonly",
                                  font=("Segoe UI", 10))
        self.e_cat.set(CATEGORIES[0])
        self.e_cat.pack(fill=tk.X, padx=10, pady=(2, 6))

        lbl("Date * (YYYY-MM-DD)").pack(fill=tk.X, padx=10)
        self.e_date = entry()
        self.e_date.insert(0, Expense.today())
        self.e_date.pack(fill=tk.X, padx=10, pady=(2, 6))

        lbl("Note (optional)").pack(fill=tk.X, padx=10)
        self.e_note = entry(); self.e_note.pack(fill=tk.X, padx=10, pady=(2, 6))

        # Buttons
        btn_row = tk.Frame(frm, bg=PANEL)
        btn_row.pack(fill=tk.X, padx=10, pady=8)

        tk.Button(btn_row, text="➕ Add", bg=SUCCESS, fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  command=self._add_expense).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(btn_row, text="💾 Save Edit", bg=ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  command=self._update_expense).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(btn_row, text="🗑️ Delete", bg=DANGER, fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  command=self._delete_expense).pack(side=tk.LEFT)

        tk.Button(btn_row, text="✖ Clear", bg=PANEL, fg=SUBTEXT, font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  command=self._clear_form).pack(side=tk.RIGHT)

    def _build_filter_section(self, parent):
        """Search + filter controls."""
        frm = tk.LabelFrame(parent, text=" 🔍  Search & Filter ", font=("Segoe UI", 10, "bold"),
                            bg=PANEL, fg=ACCENT_LT, bd=1, relief=tk.GROOVE)
        frm.pack(fill=tk.X, padx=10, pady=5)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(frm, textvariable=self.search_var, bg=ENTRY_BG, fg=TEXT,
                                insertbackground=TEXT, font=("Segoe UI", 10), relief=tk.FLAT, bd=4)
        search_entry.pack(fill=tk.X, padx=10, pady=(8, 4))

        tk.Button(frm, text="🔎 Search", bg=ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  command=self._search).pack(fill=tk.X, padx=10, pady=2)

        tk.Label(frm, text="Filter by Category:", bg=PANEL, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(fill=tk.X, padx=10, pady=(6, 0))

        self.filter_cat = ttk.Combobox(frm, values=["All"] + CATEGORIES,
                                       state="readonly", font=("Segoe UI", 10))
        self.filter_cat.set("All")
        self.filter_cat.pack(fill=tk.X, padx=10, pady=(2, 4))

        tk.Button(frm, text="⚙️ Apply Filter", bg=PANEL, fg=ACCENT_LT,
                  font=("Segoe UI", 9), relief=tk.GROOVE, padx=10, cursor="hand2",
                  command=self._apply_filter).pack(fill=tk.X, padx=10, pady=(2, 8))

    def _build_table(self, parent):
        """The main expense list (Treeview)."""
        top = tk.Frame(parent, bg=BG)
        top.pack(fill=tk.X, pady=(0, 4))

        tk.Label(top, text="📋  All Expenses", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(side=tk.LEFT)

        tk.Button(top, text="↻ Refresh", bg=PANEL, fg=SUBTEXT, font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=8, cursor="hand2",
                  command=self._load_table).pack(side=tk.RIGHT)

        cols = ("ID", "Title", "Amount", "Category", "Date", "Note")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=TEXT,
                         rowheight=28, fieldbackground=PANEL, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=ACCENT, foreground="white",
                         font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                  selectmode="browse")
        widths = [40, 200, 90, 110, 100, 180]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=tk.CENTER if col in ("ID", "Amount", "Date") else tk.W)

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Click on row → populate form for editing
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    def _build_chart_buttons(self, parent):
        """Buttons to show different charts."""
        btn_row = tk.Frame(parent, bg=BG)
        btn_row.pack(fill=tk.X, pady=6)

        tk.Label(btn_row, text="📊 Charts:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))

        charts = [
            ("🥧 Category Pie",    self._chart_pie),
            ("📈 Monthly Trend",   self._chart_monthly),
            ("📊 Category Bar",    self._chart_bar),
        ]
        for text, cmd in charts:
            tk.Button(btn_row, text=text, bg=PANEL, fg=ACCENT_LT, font=("Segoe UI", 9, "bold"),
                      relief=tk.GROOVE, padx=10, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=4)

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready.")
        bar = tk.Label(self, textvariable=self.status_var, bg=PANEL, fg=SUBTEXT,
                       font=("Segoe UI", 9), anchor="w", padx=10)
        bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ═══════════════════════ DATA OPERATIONS ═══════════════════════

    def _get_form_data(self):
        """Read and validate all form fields. Returns Expense or None."""
        title  = self.e_title.get().strip()
        amount = self.e_amount.get().strip()
        cat    = self.e_cat.get()
        date   = self.e_date.get().strip()
        note   = self.e_note.get().strip()

        if not validate_title(title):
            messagebox.showerror("Error", "Title must be 1–100 characters.")
            return None
        amount_val = validate_amount(amount)
        if amount_val is None:
            messagebox.showerror("Error", "Amount must be a positive number.")
            return None
        if not validate_date(date):
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return None

        return Expense(title=title, amount=amount_val, category=cat,
                       date_str=date, note=note)

    def _add_expense(self):
        exp = self._get_form_data()
        if exp:
            self.db.add_expense(exp)
            self._clear_form()
            self._load_table()
            self._status("✅ Expense added successfully.")

    def _update_expense(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a row to edit first.")
            return
        exp = self._get_form_data()
        if exp:
            exp.expense_id = self.selected_id
            self.db.update_expense(exp)
            self.selected_id = None
            self._clear_form()
            self._load_table()
            self._status("✏️  Expense updated.")

    def _delete_expense(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a row to delete first.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this expense?"):
            self.db.delete_expense(self.selected_id)
            self.selected_id = None
            self._clear_form()
            self._load_table()
            self._status("🗑️  Expense deleted.")

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self._load_table()
            return
        results = self.db.search_expenses(kw)
        self._populate_table(results)
        self._status(f"🔍 Found {len(results)} result(s) for '{kw}'.")

    def _apply_filter(self):
        cat = self.filter_cat.get()
        if cat == "All":
            self._load_table()
        else:
            results = self.db.get_expenses_by_category(cat)
            self._populate_table(results)
            self._status(f"📂 Showing {len(results)} expense(s) in '{cat}'.")

    # ═══════════════════════ TABLE HELPERS ═══════════════════════

    def _load_table(self):
        expenses = self.db.get_all_expenses()
        self._populate_table(expenses)
        total = self.db.get_total()
        self.total_label.config(text=f"Total: {format_currency(total)}")
        self._status(f"📋 {len(expenses)} expense(s) loaded.")

    def _populate_table(self, expenses: list):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for exp in expenses:
            tag = "odd" if expenses.index(exp) % 2 else "even"
            self.tree.insert("", tk.END, iid=str(exp.expense_id), tags=(tag,),
                             values=(exp.expense_id, exp.title,
                                     format_currency(exp.amount),
                                     exp.category, exp.date, exp.note))
        self.tree.tag_configure("odd",  background="#23233a")
        self.tree.tag_configure("even", background=PANEL)

    def _on_row_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        row_id = int(selected[0])
        vals = self.tree.item(selected[0])["values"]
        self.selected_id = row_id

        # Fill form with selected row's data
        self.e_title.delete(0, tk.END);  self.e_title.insert(0, vals[1])
        # Remove ₹ and commas before showing amount
        raw_amt = str(vals[2]).replace("₹", "").replace(",", "")
        self.e_amount.delete(0, tk.END); self.e_amount.insert(0, raw_amt)
        self.e_cat.set(vals[3])
        self.e_date.delete(0, tk.END);   self.e_date.insert(0, vals[4])
        self.e_note.delete(0, tk.END);   self.e_note.insert(0, vals[5] or "")
        self._status(f"✏️  Selected: {vals[1]}")

    def _clear_form(self):
        self.selected_id = None
        for widget in [self.e_title, self.e_amount, self.e_date, self.e_note]:
            widget.delete(0, tk.END)
        self.e_cat.set(CATEGORIES[0])
        self.e_date.insert(0, Expense.today())

    def _status(self, msg: str):
        self.status_var.set(msg)

    # ═══════════════════════ CHARTS ═══════════════════════

    def _show_chart_window(self, title: str, fig):
        """Open a chart in a separate Toplevel window."""
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=BG)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tk.Button(win, text="Close", command=win.destroy,
                  bg=DANGER, fg="white", relief=tk.FLAT,
                  font=("Segoe UI", 10)).pack(pady=6)

    def _chart_pie(self):
        data = self.db.get_category_totals()
        if not data:
            messagebox.showinfo("No Data", "No expenses to chart."); return
        fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG)
        ax.set_facecolor(BG)
        wedges, texts, autotexts = ax.pie(
            data.values(), labels=data.keys(), autopct="%1.1f%%",
            startangle=140, pctdistance=0.82,
            colors=plt.cm.Set3.colors[:len(data)]
        )
        for t in texts + autotexts:
            t.set_color(TEXT)
        ax.set_title("Spending by Category", color=TEXT, fontsize=13, fontweight="bold")
        self._show_chart_window("Category Pie Chart", fig)

    def _chart_monthly(self):
        data = self.db.get_monthly_totals()
        if not data:
            messagebox.showinfo("No Data", "No expenses to chart."); return
        labels = [format_month_label(m) for m in data.keys()]
        values = list(data.values())
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG)
        ax.set_facecolor("#1a1a2e")
        ax.plot(labels, values, marker="o", color=ACCENT_LT, linewidth=2.5,
                markerfacecolor=ACCENT, markersize=8)
        ax.fill_between(range(len(labels)), values, alpha=0.15, color=ACCENT_LT)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right", color=SUBTEXT)
        ax.tick_params(colors=SUBTEXT)
        ax.set_title("Monthly Spending Trend", color=TEXT, fontsize=13, fontweight="bold")
        ax.set_ylabel("Amount (₹)", color=SUBTEXT)
        ax.spines[:].set_color("#333355")
        fig.tight_layout()
        self._show_chart_window("Monthly Trend", fig)

    def _chart_bar(self):
        data = self.db.get_category_totals()
        if not data:
            messagebox.showinfo("No Data", "No expenses to chart."); return
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG)
        ax.set_facecolor("#1a1a2e")
        bars = ax.bar(data.keys(), data.values(),
                      color=plt.cm.Purples([0.4 + 0.6 * i / len(data) for i in range(len(data))]))
        ax.set_title("Category-wise Spending", color=TEXT, fontsize=13, fontweight="bold")
        ax.set_ylabel("Amount (₹)", color=SUBTEXT)
        ax.tick_params(colors=SUBTEXT)
        ax.spines[:].set_color("#333355")
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                    f"₹{bar.get_height():.0f}", ha="center", va="bottom",
                    color=TEXT, fontsize=8)
        fig.tight_layout()
        self._show_chart_window("Category Bar Chart", fig)
