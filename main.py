from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.metrics import dp
import sqlite3


class ExpenseTracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        # Title
        self.add_widget(Label(text="Add Expense", font_size=20))

        # Input fields
        self.amount = TextInput(hint_text='Amount', input_filter="float")
        self.category = TextInput(hint_text='Category')
        self.date = TextInput(hint_text='Date (YYYY-MM-DD)')
        self.description = TextInput(hint_text='Description')

        self.add_widget(self.amount)
        self.add_widget(self.category)
        self.add_widget(self.date)
        self.add_widget(self.description)

        # Add button
        self.add_btn = Button(text='Add Expense')
        self.add_btn.bind(on_press=self.add_expense)
        self.add_widget(self.add_btn)

        # Status message
        self.status = Label(text="", color=(0, 0.5, 0, 1))
        self.add_widget(self.status)

        # Expense list label
        self.add_widget(Label(text="Expenses List", font_size=18))

        # RecycleView setup
        self.rv = RecycleView()
        self.rv.viewclass = "Label"

        self.rv_layout = RecycleBoxLayout(
            default_size=(None, dp(40)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation='vertical'
        )
        self.rv_layout.bind(minimum_height=self.rv_layout.setter("height"))
        self.rv.layout_manager = self.rv_layout
        self.rv.add_widget(self.rv_layout)

        self.add_widget(self.rv)

        # Initialize DB and load data
        self.init_db()
        self.refresh_expense_list()

    def init_db(self):
        self.conn = sqlite3.connect('expenses.db')
        self.cursor = self.conn.cursor()

        # Create table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                amount REAL,
                category TEXT,
                date TEXT,
                description TEXT
            )
        ''')

        # Try adding new columns if DB is old
        try:
            self.cursor.execute("ALTER TABLE expenses ADD COLUMN date TEXT")
        except:
            pass
        try:
            self.cursor.execute("ALTER TABLE expenses ADD COLUMN description TEXT")
        except:
            pass

        self.conn.commit()

    def add_expense(self, instance):
        a = self.amount.text.strip()
        c = self.category.text.strip()
        d = self.date.text.strip()
        desc = self.description.text.strip()

        try:
            if a and c and d:
                self.cursor.execute(
                    "INSERT INTO expenses VALUES (?, ?, ?, ?)",
                    (float(a), c, d, desc)
                )
                self.conn.commit()
                self.status.text = f"Expense Added: {a} ({c}, {d}, {desc})"

                # Clear inputs
                self.amount.text = ""
                self.category.text = ""
                self.date.text = ""
                self.description.text = ""

                self.refresh_expense_list()
            else:
                self.status.text = "Amount, Category and Date required."
        except Exception as e:
            self.status.text = f"Error: {str(e)}"

    def refresh_expense_list(self):
        expenses = list(self.cursor.execute(
            "SELECT amount, category, date, description FROM expenses"
        ))
        self.rv.data = [
            {'text': f"{amount:.2f} | {category} | {date} | {desc}"}
            for amount, category, date, desc in expenses
        ]


class ExpenseApp(App):
    def build(self):
        self.tracker = ExpenseTracker()
        return self.tracker

    def on_stop(self):
        # Close DB safely on exit
        self.tracker.conn.close()


if __name__ == '__main__':
    ExpenseApp().run()
