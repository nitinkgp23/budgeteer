class Transaction(object):
    def __init__(self, date, desc, category, amount, account, _id):
        self.date = date  # datetime object
        self.desc = desc  # string
        self.category = category  # dropdown menu,
        self.amount = amount  # editable textbox
        self.account = account  # dropdown menu  - by default
        self.id = _id

        self.isValid = True


def convert_date(date):
    """
    Takes in date time object, returns string in format %m/%d/%Y

    becaue google sheets takes in this format
    """
    return date.strftime('%d-%B-%Y')


def negate_amount(amount):
    return '-'+amount


def update_transactions_to_sheet(sheet, transactions):
    values = [[' ', convert_date(transaction.date), transaction.desc, transaction.category,
               negate_amount(transaction.amount), transaction.account, transaction.id] for transaction in transactions]

    return sheet.insert_rows(values=values,
                             row=2,
                             # table_range='B3',
                             value_input_option='USER_ENTERED',
                             # insert_data_option='INSERT_ROWS',
                             )
