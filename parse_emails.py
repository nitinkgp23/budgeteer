from transaction import Transaction
import re
from datetime import datetime


def _parse_number(content):
    """
    Private function to return list of numbers parsed from the string.
    """
    content = content.replace(',', '')
    rr = re.findall(r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", content)
    return rr


def splitwise(message_dict):
    text = message_dict.get('Message_body')
    if not text:
        return
    text = " ".join(text.split())
    if 'You owe' not in text:
        return

    text = text[:text.index('View on Splitwise')]

    arg_dict = {'date': datetime.strptime(message_dict['Date'], '%Y-%m-%d').date(),
                'amount': _parse_number(text[text.index('You owe')+7:])[0],
                'desc': text.split('“')[1].split('”')[0],
                'account': 'Splitwise',
                '_id': None,
                'category': text[text.index(message_dict['Date'][:4]):].split()[1]
    }

    transaction = Transaction(**arg_dict)
    return transaction


def sbisavings(message_dict):
    pass


def icicicredit(message_dict):
    if 'Transaction alert' in message_dict['Subject']:
        pass

