import time, threading

from kivy.uix.screenmanager import Screen
from kivymd.uix.picker import MDDatePicker

from kivymd.app import MDApp

from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
# from kivy.uix.behaviors import T

from datetime import datetime

from kivy.lang import Builder
from kivy.loader import Loader

from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivymd.app import MDApp

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
# from kivy.uix.behaviors import T

from datetime import datetime

from backend.transaction import Transaction
from backend.main_back import auth

import pickle
import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import socket

import gspread
from backend import transaction

import time

from logger import log


class TransactionCardContent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menuitemsCategory = [{"text": "Groceries"},
                             {"text": "Transfer"},
                             {"text": "Family"},
                             {"text": "Entertainment"}]

        self.menuCategory = MDDropdownMenu(
            caller=self.ids.categoryText,
            items=menuitemsCategory,
            position="bottom",
            callback=self.set_itemCategory,
            width_mult=4,
        )

    def get_date(self, date):
        self.ids.dateText.text = date.strftime('%d-%b-%Y')

    def show_date_picker(self):
        today = datetime.today()
        if self.ids.dateText.focus:
            date_dialog = MDDatePicker(callback=self.get_date, year=today.year, month=today.month, day=today.day)
            date_dialog.open()

    def open_menuCategory(self, event=None):
        if self.ids.categoryText.focus:
            self.menuCategory.open()

    def set_itemCategory(self, instance):
        def set_item(interval):
            self.ids.categoryText.text = instance.text
            self.menuCategory.dismiss()

        set_item(0.5)               # What use is clock schedule?? I did this and it immediately happens?
        # Clock.schedule_once(set_item, 0.5)


class TransactionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transactions = iter([])
        self.finaltransactions = []
        self.button1 = MDFillRoundFlatButton(
            text="Update Transactions",
            pos_hint={"center_x": 0.5, "center_y": 0.55})

        self.button1.bind(on_release=self.get_transaction_cards)

        self.button2 = MDFillRoundFlatButton(
            text="Go Back",
            pos_hint={"center_x": 0.5, "center_y": 0.45})
        self.button2.bind(on_release=self.get_home_screen)

        self.add_widget(self.button1)
        self.add_widget(self.button2)

    def show_popup(self, title):
        # self.pop_up = PopupBox()
        # self.pop_up.update_pop_up_text('Running some task...')
        self.popup = MDDialog(title=title,
                              text="1/10",
                              size_hint=(.3, None),
                              pos_hint={"center_x": 0.5, "center_y": 0.5},
                              height=dp(200),
                              )
        self.popup.open()

    def dismiss_popup(self):
        self.popup.dismiss()

    def ignore_transaction(self, event):
        print('Ignored transaction', self.curr_transaction.desc)
        self.dialog.dismiss()

    def confirm_transaction(self, event):
        print('confirmed transaction', self.curr_transaction.desc)

        self.curr_transaction.desc = self.dialog.content_cls.ids.descText.text
        self.curr_transaction.amount = self.dialog.content_cls.ids.amountText.text
        self.curr_transaction.category = self.dialog.content_cls.ids.categoryText.text
        self.curr_transaction.account = self.dialog.content_cls.ids.accountText.text
        self.curr_transaction.date = datetime.strptime(self.dialog.content_cls.ids.dateText.text, '%d-%b-%Y')

        self.finaltransactions.append(self.curr_transaction)
        self.dialog.dismiss()

    def push_transactions(self, event=None):
        # thistime = time.time()
        # while thistime + 1 > time.time():  # 1 seconds
        #     time.sleep(1)

        # print(self.finaltransactions)
        log.info("Updating transactions to sheet")
        transaction.update_transactions_to_sheet(MDApp.get_running_app().creds['sheet'], self.finaltransactions)
        # Once the long running task is done, close the pop up.
        self.dismiss_popup()
        self.get_home_screen()

    def set_item(self, instance):
        self.screen.ids.drop_item.set_item(instance.text)
        self.menu.dismiss()

    def get_transaction_cards(self, event):

        self.curr_transaction = next(self.transactions, None)

        if not self.curr_transaction:
            self.show_popup(title="Updating transactions...")

            # Call some method that may take a while to run.
            # I'm using a thread to simulate this
            mythread = threading.Thread(target=self.push_transactions)
            mythread.start()
            return

        button_ignore = MDFlatButton(
            text="IGNORE",
            text_color=MDApp.get_running_app().theme_cls.primary_color,
        )
        button_confirm = MDFlatButton(
            text="CONFIRM", text_color=MDApp.get_running_app().theme_cls.primary_color
        )
        button_ignore.bind(on_release=self.ignore_transaction)
        button_confirm.bind(on_release=self.confirm_transaction)

        self.dialog = MDDialog(
            type="custom",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            content_cls=TransactionCardContent(),
            buttons=[button_ignore, button_confirm],
        )

        self.dialog.content_cls.ids.descText.text = self.curr_transaction.desc
        self.dialog.content_cls.ids.amountText.text = self.curr_transaction.amount
        self.dialog.content_cls.ids.categoryText.text = self.curr_transaction.category
        self.dialog.content_cls.ids.accountText.text = self.curr_transaction.account
        self.dialog.content_cls.ids.dateText.text = self.curr_transaction.date.strftime('%d-%b-%Y')

        self.dialog.bind(on_dismiss=self.get_transaction_cards)
        self.dialog.open()

    def get_home_screen(self, _=None):
        self.screen_manager.current = "home_screen"
        self.manager.transition.direction = "right"
