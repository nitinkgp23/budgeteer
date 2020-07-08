
import threading
from datetime import datetime

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog

from backend import gmailreader
from backend.transaction import Transaction
from logger import log


# from kivy.uix.behaviors import T
# from kivy.uix.behaviors import T


def transaction_factory():
    t1 = Transaction(date=datetime.today(), desc="Descrip", account="SBI", amount="500", category="Groceries",
                     _id="123")
    t2 = Transaction(date=datetime.today(), desc="hello", account="HDFC", amount="100", category="Groceries", _id="11")
    t3 = Transaction(date=datetime.today(), desc="bye", account="Splitwise", amount="20", category="Transfer", _id="2")
    data = [t1, t2, t3]
    return iter(data), len(data)


class HomeScreen(Screen):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        button1 = MDFillRoundFlatButton(
            text="Update Transactions",
            pos_hint={"center_x": 0.5, "center_y": 0.55})

        button1.bind(on_release=self.get_transactions_screen)
        self.add_widget(button1)

    def get_summary_screen(self, _=None):
        pass

    def show_popup(self, title):
        # self.pop_up = PopupBox()
        # self.pop_up.update_pop_up_text('Running some task...')
        self.dialog = MDDialog(title=title,
                               text="1/10",
                               size_hint=(.3, None),
                               pos_hint={"center_x": 0.5, "center_y": 0.5},
                               height=dp(200),
                               )
        self.dialog.open()

    def dismiss_popup(self):
        self.dialog.dismiss()

    def get_transactions_screen(self, _=None):
        self.show_popup(title="Fetching transactions...")

        # Call some method that may take a while to run.
        # I'm using a thread to simulate this
        mythread = threading.Thread(target=self.fetch_transactions)
        mythread.start()

    def fetch_transactions(self):
        # thistime = time.time()
        # while thistime + 1 > time.time():  # 1 seconds
        #     time.sleep(1)
        log.info("Retrieving new gmail messages")
        transactions = gmailreader.get_messages(MDApp.get_running_app().creds['service'])
        # Once the long running task is done, close the pop up.
        self.dismiss_popup()

        transactions, num_transactions = iter(transactions), len(transactions)
        self.screen_manager.get_screen('transaction_screen').transactions = transactions
        self.screen_manager.get_screen('transaction_screen').button1.text = \
            "Update {} Transactions".format(num_transactions)

        print(MDApp.get_running_app().creds)
        # And then go to transaction screen
        self.screen_manager.current = "transaction_screen"
        self.manager.transition.direction = "left"
