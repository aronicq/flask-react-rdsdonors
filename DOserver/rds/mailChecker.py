from __future__ import print_function

import sqlite3
import sys
import traceback
from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import datetime, pytz
from bs4 import BeautifulSoup
import dateutil.parser as parser

# If modifying these scopes, delete the file token.json.
# разрешаем доступ во все области ко всем действиям в почте(добавления ярлыков, чтение, отправка писем и тд)
SCOPES = 'https://mail.google.com/'

label_id_one = 'Label_6'
label_id_two = 'UNREAD'


def add_daily_payment(conn, payment):
    sql_add_project = """ INSERT INTO dailypayments (time_date, times_that_day, amount)
                        VALUES(?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql_add_project, payment)
    conn.commit()


def add_payment(conn, payment):
    sql_add_project = """ INSERT INTO payments (time_date, email, city, amount)
                    VALUES(?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql_add_project, payment)
    conn.commit()


def get_credits():
    # use saved token and credentials constructed for our app
    store = file.Storage(r'token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/home/user/Dropbox/flask-react-rdsdonors/DOserver/rds/credentials.json',
                                              SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service


def filter_date_from(msg):
    result = False
    msg_date = msg_from = ""
    for i in msg['payload']['headers']:
        if i['name'] == "From":
            msg_from = i['value']
        if i['name'] == "Date":
            msg_date = i['value']

    if msg_from == '"Yandex.Money Payment Center" <paymentcenter@yamoney.ru>' and \
            datetime.datetime.strptime(msg_date, "%a, %d %b %Y %X %z (%Z)") > datetime.datetime(2020, 2, 29).replace(
        tzinfo=pytz.timezone('Europe/Moscow')):
        result = True

    return result


def force_check():
    service = get_credits()
    msgs_ids = service.users().messages().list(userId='me', maxResults=400).execute()['messages']
    msgs = [service.users().messages().get(userId="me", id=mess['id']).execute() for mess in msgs_ids]
    yandex_msgs = [msg for msg in msgs if filter_date_from(msg)]

    print()


def regular_check(conn):
    service = get_credits()

    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    unread_msgs = service.users().messages().list(userId='me', labelIds=[label_id_two]).execute()

    # We get a dictonary. Now reading values for the key 'messages'
    mssg_list = unread_msgs['messages']

    print("Total messages taken from inbox: ", str(len(mssg_list)))

    final_list = []
    donations_per_day = {}
    # going through list of al messages

    for mssg in mssg_list:
        temp_dict = {}
        m_id = mssg['id']  # get id of individual message
        message = service.users().messages().get(userId="me", id=m_id).execute()  # fetch the message using API
        payld = message['payload']  # get payload of the message
        headr = payld['headers']  # get header of the payload
        msg_from = ""
        msg_subject = ""
        msg_date = ""
        msg_text = ""

        def get_attachments():
            try:
                msg_id = mssg['id']
                message = service.users().messages().get(userId='me', id=msg_id).execute()

                for part in message['payload'].get('parts', ''):
                    if part['filename']:
                        if 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            att_id = part['body']['attachmentId']
                            att = service.users().messages().attachments().get(userId='me', messageId=msg_id,
                                                                               id=att_id).execute()
                            data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = part['filename']
                with open(path, 'wb') as f:
                    f.write(file_data)
                return file_data

            except errors.HttpError as error:
                print('An error occurred: %s' % error)

        def create_message(body="", subj=""):
            message = MIMEMultipart()
            message['to'] = "efim002@gmail.com, sofya.klimova@gmail.com"
            message['from'] = "rsbor.ru@gmail.com"
            message.attach(MIMEText(body))
            message['subject'] = subj
            file_data = get_attachments()
            attachedfile = MIMEApplication(file_data, _subtype="pdf", _encoder=encode_base64)
            attachedfile.add_header('content-disposition', 'attachment', filename=temp_dict['Subject'] + ".pdf")
            message.attach(attachedfile)
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        for one in headr:
            # getting the Subject
            if one['name'] == 'Subject':
                msg_subject = one['value']
                temp_dict['Subject'] = msg_subject
            # getting date
            if one['name'] == 'Date':
                msg_date = one['value']
                date_parse = (parser.parse(msg_date))
                m_date = (date_parse.date())
                temp_dict['Date'] = str(m_date)
            # getting the Sender
            if one['name'] == 'From':
                msg_from = one['value']
                temp_dict['Sender'] = msg_from
        # print("gettings")
        # письмо отправлено нами, пропускаем, не нужно нам
        if msg_from == 'Razdelny Sbor <rsbor.ru@gmail.com>': continue
        if "paymentcenter@yamoney.ru" not in msg_from and "shoppay@yamoney.ru" not in msg_from:
            continue

        temp_dict['Snippet'] = message['snippet']  # fetching message snippet
        try:
            # print("-2")
            # Fetching message body
            mssg_parts = payld['parts']  # fetching the message parts
            part_one = mssg_parts[0]
            # if part_one['filename'] == "":
            #     part_one = mssg_parts[1]
            # print("-1")
            # fetching first element of the part
            part_body = part_one['body']  # fetching body of the message
            try:
                part_data = part_body['data']
            except:
                part_body = part_one['parts'][1]
            finally:
                try:
                    part_body = part_body['body']
                    part_data = part_body['data']  # fetching data from the body
                except:
                    pass

            # print("0")
            clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
            clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
            # print("1")
            clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
            # print("2")
            # print(bs4.__version__)
            soup = BeautifulSoup(clean_two, "lxml")
            # print("soup")
            mssg_body = soup.body()
            # mssg_body is a readible form of message body
            # depending on the end user's requirements, it can be further cleaned
            # using regex, beautiful soup, or any other method
            temp_dict['Message_body'] = mssg_body
            # print(mssg_body)
            msg_text = mssg_body[0].text.lower()

        except:
            # pass
            try:
                exc_info = sys.exc_info()
            finally:
                traceback.print_exception(*exc_info)

        # print(temp_dict)
        final_list.append(temp_dict)  # This will create a dictonary item in the final list

        # branch payments acts or returns
        if "Subject" in temp_dict and 'РЕЕСТР ПЛАТЕЖЕЙ В «РазДельный Сбор» www.rsbor.ru' in temp_dict['Subject']:

            if "РЕЕСТР ПЛАТЕЖЕЙ В «РазДельный Сбор» www.rsbor.ru. № 20" in temp_dict['Subject']:
                print()

            # if service.users().messages()
            # service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()
            # generator which separates email into pieces and returns lines with donate info by symbol "@"
            lines_of_donations = [[i] for i in soup.contents[0].contents[0].contents[0].contents[0].split("; \r\n") if
                                  "@" in i]
            if len([[i] for i in soup.contents[0].contents[0].contents[0].contents[0].split("\r\n") if
                    "Номер транзакции" in i][0][0].split(";")) == 11:
                comment_field = 9
            else:
                comment_field = 10

            # finds city in comments, returns spb by defult and city that list and comment contains
            #  IT LOWERS THE LETTERS

            def define_city(str):
<<<<<<< HEAD
                words = ["хабаровск", "хабаровска", "владивосток", "владивостока",
                         "череповец", "череповца", "красная поляна", "красной поляны",
                         "сочи", "сочи", "воронеж", "воронежа", "рсограмота", "грамота", "глушкина", "глушкиной"]
=======

                words = ["артёма", "артем",
                         "артём", "артема",
                         "белорецк", "белорецка",
                         "благовещенск", "благовещенска",
                         "владивосток", "владивостока",
                         "воронеж", "воронежа",
                         "краснодар", "краснодара",
                         "липецк", "липецка",
                         "сочи", "сочи",
                         "сургут", "сургута",
                         "торжок", "торжка",
                         "хабаровск", "хабаровска",
                         "череповец", "череповца",
                         "новгород", "новгорода",
                         "красная поляна", "красной поляны",

                         "всеволожск", "всеволожска",
                         "гатчина", "гатчины",
                         "ивангород", "ивангорода",
                         "кингисепп", "кингисеппа",
                         "кириши", "киришей",
                         "колтуши", "колтушей",
                         "кудрово", "кудрова",
                         "сосновый бор", "соснового бора",

                         "рсограмота", "грамота", ]
>>>>>>> e1657004dccd805f50105708a0e6b49e78213394

                try:
                    city = [words.index(i) for i in words if i in str.lower()][0]
                    return words[city - bool(city % 2 != 0)]
                except:
                    return "Санкт-Петербург"

            date_time = 0
            daily_don = 0
            for i in range(len(lines_of_donations)):
                tmp, email, sum, tmp, tmp, date_time = lines_of_donations[i][0].split(";")[0:6]
                print(lines_of_donations[i][0].split(";"))
                city = define_city(lines_of_donations[i][0].split(";")[comment_field])
                add_payment(conn, (date_time, email, city, int(sum.split(".")[0])))
                daily_don += int(sum.split(".")[0])

            add_daily_payment(conn, (date_time, len(lines_of_donations), daily_don))
            # This will mark the message as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()

            print(temp_dict)

        if "Subject" in temp_dict and 'РЕЕСТР ВОЗВРАТОВ ОТ «РазДельный Сбор» www.rsbor.ru' in temp_dict['Subject']:
            if "сумма возвратов: 0.00" not in msg_text:
                message = create_message(body=msg_text, subj=msg_subject)
                service.users().messages().send(userId='me', body=message).execute()
            # This will mark the message as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            # if service.users().messages()
            service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

        if "Subject" in temp_dict and "Акт оказанных услуг по договору" in temp_dict['Subject']:
            message = create_message(body=msg_text, subj=msg_subject)
            service.users().messages().send(userId='me', body=message).execute()
            # This will mark the messagea as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            # if service.users().messages()
            service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

    print("Total messaged retrived: ", str(len(final_list)))
    return donations_per_day


if __name__ == '__main__':
    conn = sqlite3.connect("../dbfiles/db_file.db")
    regular_check(conn)
from __future__ import print_function

import sqlite3
import sys
import traceback
from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import datetime, pytz
from bs4 import BeautifulSoup
import dateutil.parser as parser

# If modifying these scopes, delete the file token.json.
# разрешаем доступ во все области ко всем действиям в почте(добавления ярлыков, чтение, отправка писем и тд)
SCOPES = 'https://mail.google.com/'

label_id_one = 'Label_6'
label_id_two = 'UNREAD'


def add_daily_payment(conn, payment):
    sql_add_project = """ INSERT INTO dailypayments (time_date, times_that_day, amount)
                        VALUES(?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql_add_project, payment)
    conn.commit()


def add_payment(conn, payment):
    sql_add_project = """ INSERT INTO payments (time_date, email, city, amount)
                    VALUES(?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql_add_project, payment)
    conn.commit()


def get_credits():
    # use saved token and credentials constructed for our app
    store = file.Storage(r'token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/home/user/Dropbox/flask-react-rdsdonors/DOserver/rds/credentials.json',
                                              SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service


def filter_date_from(msg):
    result = False
    msg_date = msg_from = ""
    for i in msg['payload']['headers']:
        if i['name'] == "From":
            msg_from = i['value']
        if i['name'] == "Date":
            msg_date = i['value']

    if msg_from == '"Yandex.Money Payment Center" <paymentcenter@yamoney.ru>' and \
            datetime.datetime.strptime(msg_date, "%a, %d %b %Y %X %z (%Z)") > datetime.datetime(2020, 2, 29).replace(
        tzinfo=pytz.timezone('Europe/Moscow')):
        result = True

    return result


def force_check():
    service = get_credits()
    msgs_ids = service.users().messages().list(userId='me', maxResults=400).execute()['messages']
    msgs = [service.users().messages().get(userId="me", id=mess['id']).execute() for mess in msgs_ids]
    yandex_msgs = [msg for msg in msgs if filter_date_from(msg)]

    print()


def regular_check(conn):
    service = get_credits()

    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    unread_msgs = service.users().messages().list(userId='me', labelIds=[label_id_two]).execute()

    # We get a dictonary. Now reading values for the key 'messages'
    mssg_list = unread_msgs['messages']

    print("Total messages taken from inbox: ", str(len(mssg_list)))

    final_list = []
    donations_per_day = {}
    # going through list of al messages

    for mssg in mssg_list:
        temp_dict = {}
        m_id = mssg['id']  # get id of individual message
        message = service.users().messages().get(userId="me", id=m_id).execute()  # fetch the message using API
        payld = message['payload']  # get payload of the message
        headr = payld['headers']  # get header of the payload
        msg_from = ""

        def get_attachments():
            try:
                msg_id = mssg['id']
                message = service.users().messages().get(userId='me', id=msg_id).execute()

                for part in message['payload'].get('parts', ''):
                    if part['filename']:
                        if 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            att_id = part['body']['attachmentId']
                            att = service.users().messages().attachments().get(userId='me', messageId=msg_id,
                                                                               id=att_id).execute()
                            data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = part['filename']
                with open(path, 'wb') as f:
                    f.write(file_data)
                return file_data

            except errors.HttpError as error:
                print('An error occurred: %s' % error)

        def create_message(body="", subj=""):
            message = MIMEMultipart()
            message['to'] = "efim002@gmail.com, sofya.klimova@gmail.com"
            message['from'] = "rsbor.ru@gmail.com"
            message.attach(MIMEText(body))
            message['subject'] = subj
            file_data = get_attachments()
            attachedfile = MIMEApplication(file_data, _subtype="pdf", _encoder=encode_base64)
            attachedfile.add_header('content-disposition', 'attachment', filename=temp_dict['Subject'] + ".pdf")
            message.attach(attachedfile)
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        for one in headr:
            # getting the Subject
            if one['name'] == 'Subject':
                msg_subject = one['value']
                temp_dict['Subject'] = msg_subject
            # getting date
            if one['name'] == 'Date':
                msg_date = one['value']
                date_parse = (parser.parse(msg_date))
                m_date = (date_parse.date())
                temp_dict['Date'] = str(m_date)
            # getting the Sender
            if one['name'] == 'From':
                msg_from = one['value']
                temp_dict['Sender'] = msg_from
        # письмо отправлено нами, пропускаем, не нужно нам
        if msg_from == 'Razdelny Sbor <rsbor.ru@gmail.com>': continue
        if "paymentcenter@yamoney.ru" not in msg_from and "shoppay@yamoney.ru" not in msg_from:
            continue

        temp_dict['Snippet'] = message['snippet']  # fetching message snippet
        try:
            # Fetching message body
            mssg_parts = payld['parts']  # fetching the message parts
            part_one = mssg_parts[0]
            # fetching first element of the part
            part_body = part_one['body']  # fetching body of the message
            try:
                part_data = part_body['data']
            except:
                part_body = part_one['parts'][1]
            finally:
                try:
                    part_body = part_body['body']
                    part_data = part_body['data']  # fetching data from the body
                except:
                    pass

            clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
            clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8

            clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8

            soup = BeautifulSoup(clean_two, "lxml")

            mssg_body = soup.body()
            # mssg_body is a readible form of message body
            # depending on the end user's requirements, it can be further cleaned
            # using regex, beautiful soup, or any other method
            temp_dict['Message_body'] = mssg_body

            msg_text = mssg_body[0].text.lower()

        except:
            # pass
            try:
                exc_info = sys.exc_info()
            finally:
                traceback.print_exception(*exc_info)


        final_list.append(temp_dict)  # This will create a dictonary item in the final list

        # branch payments acts or returns
        if "Subject" in temp_dict and 'РЕЕСТР ПЛАТЕЖЕЙ В «РазДельный Сбор» www.rsbor.ru' in temp_dict['Subject']:

            if "РЕЕСТР ПЛАТЕЖЕЙ В «РазДельный Сбор» www.rsbor.ru. № 20" in temp_dict['Subject']:
                print()

            # if service.users().messages()
            # service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()
            # generator which separates email into pieces and returns lines with donate info by symbol "@"
            lines_of_donations = [[i] for i in soup.contents[0].contents[0].contents[0].contents[0].split("; \r\n") if
                                  "@" in i]
            if len([[i] for i in soup.contents[0].contents[0].contents[0].contents[0].split("\r\n") if
                    "Номер транзакции" in i][0][0].split(";")) == 11:
                comment_field = 9
            else:
                comment_field = 10

            # finds city in comments, returns spb by defult and city that list and comment contains
            #  IT LOWERS THE LETTERS

            def define_city(str):

                words = ["артёма", "артем",
                         "артём", "артема",
                         "белорецк", "белорецка",
                         "благовещенск", "благовещенска",
                         "владивосток", "владивостока",
                         "воронеж", "воронежа",
                         "краснодар", "краснодара",
                         "липецк", "липецка",
                         "сочи", "сочи",
                         "сургут", "сургута",
                         "торжок", "торжка",
                         "хабаровск", "хабаровска",
                         "череповец", "череповца",
                         "новгород", "новгорода",
                         "красная поляна", "красной поляны",

                         "всеволожск", "всеволожска",
                         "гатчина", "гатчины",
                         "ивангород", "ивангорода",
                         "кингисепп", "кингисеппа",
                         "кириши", "киришей",
                         "колтуши", "колтушей",
                         "кудрово", "кудрова",
                         "сосновый бор", "соснового бора",

                         "рсограмота", "грамота",
                         
                         "глушкина", "глушкиной", ]

                try:
                    city = [words.index(i) for i in words if i in str.lower()][0]
                    return words[city - bool(city % 2 != 0)]
                except:
                    return "Санкт-Петербург"

            date_time = 0
            daily_don = 0
            for i in range(len(lines_of_donations)):
                tmp, email, sum, tmp, tmp, date_time = lines_of_donations[i][0].split(";")[0:6]
                print(lines_of_donations[i][0].split(";"))
                city = define_city(lines_of_donations[i][0].split(";")[comment_field])
                add_payment(conn, (date_time, email, city, int(sum.split(".")[0])))
                daily_don += int(sum.split(".")[0])

            add_daily_payment(conn, (date_time, len(lines_of_donations), daily_don))
            # This will mark the message as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()

            print(temp_dict)

        if "Subject" in temp_dict and 'РЕЕСТР ВОЗВРАТОВ ОТ «РазДельный Сбор» www.rsbor.ru' in temp_dict['Subject']:
            if "сумма возвратов: 0.00" not in msg_text:
                message = create_message(body=msg_text, subj=msg_subject)
                service.users().messages().send(userId='me', body=message).execute()
            # This will mark the message as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            # if service.users().messages()
            service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

        if "Subject" in temp_dict and "Акт оказанных услуг по договору" in temp_dict['Subject']:
            message = create_message(body=msg_text, subj=msg_subject)
            service.users().messages().send(userId='me', body=message).execute()
            # This will mark the messagea as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            # if service.users().messages()
            service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

    print("Total messaged retrived: ", str(len(final_list)))
    return donations_per_day


if __name__ == '__main__':
    conn = sqlite3.connect("../dbfiles/db_file.db")
    regular_check(conn)

