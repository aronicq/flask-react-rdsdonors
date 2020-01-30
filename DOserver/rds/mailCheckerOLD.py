from __future__ import print_function

from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import dateutil.parser as parser

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://mail.google.com/'


def check():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    label_id_one = 'Label_6'
    label_id_two = 'UNREAD'

    # Getting all the unread messages from Inbox
    # labelIds can be changed accordingly
    unread_msgs = service.users().messages().list(userId='me', labelIds=[
                                                                            label_id_two
                                                                        ]).execute()

    # We get a dictonary. Now reading values for theh key 'messages'
    mssg_list = unread_msgs['messages']

    print("Total messages taken from inbox: ", str(len(mssg_list)))

    final_list = []

    for mssg in mssg_list:
        temp_dict = {}
        m_id = mssg['id']  # get id of individual message
        message = service.users().messages().get(userId="me", id=m_id).execute()  # fetch the message using API
        payld = message['payload']  # get payload of the message
        headr = payld['headers']  # get header of the payload
        msg_from = ""
        msg_text = ""
        payments = []

        for one in headr:  # getting the Subject
            if one['name'] == 'Subject':
                msg_subject = one['value']
                temp_dict['Subject'] = msg_subject
            else:
                pass


        for two in headr:  # getting the date
            if two['name'] == 'Date':
                try:
                    msg_date = two['value']
                    date_parse = (parser.parse(msg_date))
                    m_date = (date_parse.date())
                    temp_dict['Date'] = str(m_date)
                except: pass
            else:
                pass

        for three in headr:  # getting the Sender
            if three['name'] == 'From':
                msg_from = three['value']
                temp_dict['Sender'] = msg_from
            else:
                pass

        # письмо не наше, не нужно нам
        if msg_from == 'Razdelny Sbor <rsbor.ru@gmail.com>': continue

        temp_dict['Snippet'] = message['snippet']  # fetching message snippet

        try:

            # Fetching message body
            mssg_parts = payld['parts']  # fetching the message parts
            part_one = mssg_parts[0]  # fetching first element of the part
            part_body = part_one['body']  # fetching body of the message
            try:
                part_data = part_body['data']

            except:
                part_body = part_one['parts'][0]
                part_body = part_body['body']

            part_data = part_body['data']  # fetching data from the body
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
            pass
        #
        # print(temp_dict)
        final_list.append(temp_dict)  # This will create a dictonary item in the final list
        #
        # if "Сумма возвратов: 0.00" in msg_text: continue

        if "Subject" in temp_dict and 'РЕЕСТР ПЛАТЕЖЕЙ В «РазДельный Сбор» www.rsbor.ru' in temp_dict['Subject']:
            print(temp_dict)

            def create_payment(sum, currency, sender_id):
                return [sender_id, sum]

            def create_message(body, subj):
                message = MIMEMultipart()
                message['to'] = "efim002@gmail.com, sofya.klimova@gmail.com "
                message['from'] = "rsbor.ru@gmail.com"
                message.attach(MIMEText(body))
                message['subject'] = subj

                return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            words = ["хабаровск", "хабаровска",
                     "владивосток", "владивостока",
                     "череповца", "череповец",
                     "красная поляна", "красной поляны",
                     "сочи",
                     "воронеж",
                     "музей",
                     "командировки", "поездки",
                     "регионы", "доклад"]
            # красная поляна, сочи, музей, командировки, поездки, регионы, доклад, перевод
            key_words = [line for line in msg_text.split("\n") if any(word in line for word in words)]
            if key_words != []:
                message = create_message(subj = msg_subject, body = "\n".join(key_words))
                service.users().messages().send(userId='me', body=message).execute()

            # This will mark the messagea as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            # if service.users().messages()
            # service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

        if "Subject" in temp_dict and 'РЕЕСТР ВОЗВРАТОВ ОТ «РазДельный Сбор» www.rsbor.ru' in temp_dict['Subject']:
            print(temp_dict)
            #final_list.append(temp_dict)  # This will create a dictonary item in the final list

            def create_message():
                message = MIMEMultipart()
                message['to'] = "efim002@gmail.com, sofya.klimova@gmail.com "
                message['from'] = "rsbor.ru@gmail.com"
                message.attach(MIMEText(msg_text))

                return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

            if "сумма возвратов: 0.00" not in msg_text:
                message = create_message()
                service.users().messages().send(userId='me', body=message).execute()
        # This will mark the messagea as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            # if service.users().messages()
            # service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

        if "Subject" in temp_dict and "Акт оказанных услуг по договору" in temp_dict['Subject']:
            print(temp_dict)
            #final_list.append(temp_dict)  # This will create a dictonary item in the final list

            def create_message():
                message = MIMEMultipart()
                message['to'] = "efim002@gmail.com, sofya.klimova@gmail.com "
                message['from'] = "rsbor.ru@gmail.com"
                message.attach(MIMEText(msg_text))

                file_data = get_attachments()

                attachedfile = MIMEApplication(file_data, _subtype="pdf", _encoder=encode_base64)
                attachedfile.add_header('content-disposition', 'attachment', filename=temp_dict['Subject'] + ".pdf")
                message.attach(attachedfile)

                return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

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

            message = create_message()
            service.users().messages().send(userId='me', body=message).execute()
        # This will mark the messagea as read
            service.users().messages().modify(userId='me', id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()
            #if service.users().messages()
            service.users().messages().modify(userId='me', id=m_id, body={'addLabelIds': [label_id_one]}).execute()

    print("Total messaged retrived: ", str(len(final_list)))
    return final_list

if __name__ == '__main__':
    check()
