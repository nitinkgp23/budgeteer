from __future__ import print_function
import pickle
import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import socket

import gspread
import gmailreader
import transaction
import gui

from logger import log

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/gmail.readonly']

SHEET_ID = '1__g3p95s-w7dWAG7AlXMaxsk8oH9-ZxUhhBTyWjZwa0'


def auth():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('files/token.pickle'):
        with open('files/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'files/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('files/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def wait_for_internet_connection():
    while True:
        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            pass

        return False


def initialise_app():
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

    return service, sheet, categories, accounts


def main():
    log.info("App running")
    service, sheet, categories, accounts = initialise_app()
    log.info("App initialised")

    log.info("Retrieving new gmail messages")
    transactions = gmailreader.get_messages(service)
    if transactions:
        log.info("New transactions found. Opening GUI for user input")
        transactions = gui.update_transactions_via_gui(transactions, categories, accounts)
        log.info("Updating transactions to sheet")
        transaction.update_transactions_to_sheet(sheet, transactions)

    else:
        log.info("No new transactions found")

    log.info("Process completed")


if __name__ == '__main__':
    main()
