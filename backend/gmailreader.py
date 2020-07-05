from __future__ import print_function

import os
import pickle
import base64
import json

import dateutil.parser as parser
from bs4 import BeautifulSoup

from backend import parse_emails


def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    except Exception as e:
        print(e)


def get_last_read_email():
    if os.path.exists('/Users/nitinchoudhary/budgeteer/files/last_read.pickle'):
        with open('/Users/nitinchoudhary/budgeteer/files/last_read.pickle', 'rb') as token:
            message_id = pickle.load(token)

        return message_id
    else:
        return None


def read_email(service, user_id, mssg):
    temp_dict = {}
    m_id = mssg['id']  # get id of individual message
    message = service.users().messages().get(userId=user_id, id=m_id).execute()  # fetch the message using API
    payld = message['payload']  # get payload of the message
    headr = payld['headers']  # get header of the payload

    for one in headr:  # getting the Subject
        if one['name'] == 'Subject':
            msg_subject = one['value']
            temp_dict['Subject'] = msg_subject
        else:
            pass

    for two in headr:  # getting the date
        if two['name'] == 'Date':
            msg_date = two['value']
            date_parse = (parser.parse(msg_date))
            m_date = (date_parse.date())
            temp_dict['Date'] = str(m_date)
        else:
            pass

    for three in headr:  # getting the Sender
        if three['name'] == 'From':
            msg_from = three['value']
            temp_dict['Sender'] = msg_from
        else:
            pass

    temp_dict['Snippet'] = message['snippet']  # fetching message snippet

    try:
        # Fetching message body
        mssg_parts = payld['parts']  # fetching the message parts
        part_one = mssg_parts[0]  # fetching first element of the part
        part_body = part_one['body']  # fetching body of the message
        part_data = part_body['data']  # fetching data from the body
        clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
        clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
        soup = BeautifulSoup(clean_two, "lxml")
        mssg_body = soup.contents[0].text
        # mssg_body is a readible form of message body
        # depending on the end user's requirements, it can be further cleaned
        # using regex, beautiful soup, or any other method
        temp_dict['Message_body'] = mssg_body

    except:
        pass

    return temp_dict


def parse_transaction(service, user_id, mssg):
    message_dict = read_email(service, user_id, mssg)
    sender = message_dict['Sender']
    if 'hello@splitwise.com' in sender:
        return parse_emails.splitwise(message_dict)

    elif sender == 'credit_cards@icicibank.com':
        return parse_emails.icicicredit(message_dict)

    elif sender == 'sbisavings':
        return parse_emails.sbisavings(message_dict)


def get_messages(service):
    user_id = 'me'
    with open('/Users/nitinchoudhary/budgeteer/files/emails.json') as f:
        emails = json.load(f)['emails']
    query = 'from:('
    for email in emails[:-1]:
        query += email + ' OR '
    query += emails[-1] + ')'
    messages = ListMessagesMatchingQuery(service, user_id, query)
    last_read_message_id = get_last_read_email()
    new_last_read = None
    final_list = []

    transactions = []
    for mssg in messages:
        if mssg['id'] == last_read_message_id:
            break

        transaction = parse_transaction(service, user_id, mssg)
        if transaction:
            transactions.append(transaction)

    new_last_read = messages[0]['id']

    with open('/Users/nitinchoudhary/budgeteer/files/last_read.pickle', 'wb') as token:
        pickle.dump(new_last_read, token)

    return transactions
