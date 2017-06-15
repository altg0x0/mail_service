import email
import re
import email.parser as parser
import email.utils
import email.header

def decode_email(msg):
    decoded_message = ''
    for part in msg.walk():
        charset = part.get_content_charset;
        if part.get_content_type() == 'text/plain':
            part_str = part.get_payload(decode=1)
            decoded_message += part_str.decode(charset)
    return decoded_message

def decod(h):
    s = email.header.decode_header(h)[0]
    return str(s[0], s[1]) if s[1] else s[0]

class letter():
    par = parser.BytesParser()
    message = None
    attachments = []
    body = ''
    path = ''
    date_received = None

    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            msg = letter.par.parse(f)
            self.date_received = email.utils.parsedate_to_datetime(
            msg['received'].split(';')[1])
            attachments = []
            body = None
            for part in msg.walk():
              if part.get_content_type().startswith('multipart/'):
                continue
              try:
                filename = part.get_filename()
              except:
                filename = 'Mail attachment'
              if part.get_content_type() == "text/plain" and not body:
                body = part.get_payload(decode=True).decode(part.get_content_charset())
              elif filename is not None:
                content_type = part.get_content_type()
                #attachments.append(ContentFile(part.get_payload(decode=True), filename))
            if body is None:
                body = ''
            self.body = body
            self.message = msg

    def __getitem__(self, it : str):
        if it.startswith('short_'):
            ret = self.__getitem(it[6:])
            if len(ret) > 150:
                return ret[:120] + ' …'
            return ret
        return self.__getitem(it)

    def __getitem(self, it):
        if it == 'from_real_name':
            return decod(email.utils.parseaddr(self.message['From'])[0])
        if it == 'from_address':
            return email.utils.parseaddr(self.message['From'])[1]
        if it == 'to_address':
            return email.utils.parseaddr(self.message['To'])[1]
        if it == 'to_real_name':
            return decod(email.utils.parseaddr(self.message['To'])[0])
        if it == 'body':
            return self.body
        if it == 'date':
            return self.date_received.strftime('%H:%M:%S %d.%m.%Y')
        if it == 'subject':
            try:
                return decod(self.message['Subject'])
            except Exception:
                return 'ERROR'
        return 'UNKNOWN ATTRIBUTE'
