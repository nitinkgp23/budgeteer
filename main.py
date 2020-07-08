# print("Python : Inside app")

from datetime import datetime

import gspread
from googleapiclient.discovery import build
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.loader import Loader
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from layout.screens import HomeScreen, SummaryScreen, TransactionScreen
from backend.main_back import auth
from backend.transaction import Transaction

from logger import log

# from kivy.uix.behaviors import T

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/gmail.readonly']

SHEET_ID = '1__g3p95s-w7dWAG7AlXMaxsk8oH9-ZxUhhBTyWjZwa0'


def transaction_factory():
    t1 = Transaction(date=datetime.today(), desc="Descrip", account="SBI", amount="500", category="Groceries",
                     _id="123")
    t2 = Transaction(date=datetime.today(), desc="hello", account="HDFC", amount="100", category="Groceries", _id="11")
    t3 = Transaction(date=datetime.today(), desc="bye", account="Splitwise", amount="20", category="Transfer", _id="2")
    data = [t1, t2, t3]
    return iter(data), len(data)


class SpinnerMDDialog(BoxLayout):
    pass


class WindowManager(ScreenManager):
    pass


class ContentNavigationDrawer(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class BudgeteerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Teal"
        self.dialog_change_theme = None
        self.toolbar = None
        self.root_widget = None
        self.data_screens = {}
        Loader.loading_image = f"assets/logo/kivymd_logo.png"
        self.creds = {}

    def build(self):
        # self.theme_cls.theme_style = "Dark"
        self.root_widget = Builder.load_file("my.kv")
        # Clock.schedule_once(self.screen_switch_one, 36)  # clock callback for the first screen
        # Clock.schedule_once(self.screen_switch_two, 4)  # clock callback for the second screen
        # self.initialise_app()
        Clock.schedule_once(self.initialise_app)
        # print("Hello")
        return self.root_widget

    def initialise_app(self, event=None):
        log.info("Initialising app..")
        # wait_for_internet_connection()

        # authorize app to read emails
        log.info("Getting gmail credentials and building service")
        creds = auth()
        service = build('gmail', 'v1', credentials=creds, cache_discovery=False)

        # authorize app to access google sheets
        log.info("Getting sheets credentials and building service")
        gc = gspread.oauth()
        sheet = gc.open_by_key(SHEET_ID).worksheet('Transactions')
        categories = gc.open_by_key(SHEET_ID).worksheet('Categories').col_values(1)[1:]
        accounts = gc.open_by_key(SHEET_ID).worksheet('Balance History').col_values(4)[1:]

        self.creds = {'service': service,
                      'sheet': sheet,
                      'categories': categories,
                      'accounts': accounts}


if __name__ == "__main__":
    BudgeteerApp().run()
