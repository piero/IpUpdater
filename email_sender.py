import smtplib as smtp
from logger import Logger
from email.mime.text import MIMEText
import re

class EmailSender:
    
    def __init__(self,
                host,
                port,
                username,
                password,
                timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
    
    
    def send(self, from_addr, to_addr, subject, text):
        msg = MIMEText(text)
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        try:
            server = smtp.SMTP(host=self.host,
                               port=self.port,
                               timeout=self.timeout)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
        
        except Exception, e:
            print '[!] Error sending email to %s: %s' % (to_addr, str(e))
    

    def isValidEmailAddress(self, addr):
        EMAIL_REGEX = re.compile(r"^.+@.+\..{2,3}$")
        if addr is None or not EMAIL_REGEX.match(addr):
            return False
        return True