import os
import smtplib
from threading import Thread, Lock
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailbomb:

    def __init__(self, host : str, port : int, login : str, key : str, log='mailbomb.log'):

        print("Launching new Mailbomb...")
        self.messageEditLock = Lock()
        self.message = MIMEMultipart()
        self.targetQueueLock = Lock()
        self.host = host
        self.port = port
        self.login = login
        self.key = key
        self.agents = []
        self.targets = []
        self.message_raw = None
        self.headers = {}
        self.options = {}
        self.missed = []
        self.log = log


    def load_target_list(self, filepath : str):

        filename, file_extension = os.path.splitext(filepath)
        file_extension_lower = file_extension.lower()
        if file_extension_lower == '.txt':

            with open(filepath, 'r', encoding='UTF-8') as target_list:

                for target in target_list:

                    self.add_target(target.strip())

                target_list.close()

        else:

            raise ValueError('Unsupported filetype: ' + filename + file_extension)


    def add_target(self, target : str):

        self.targetQueueLock.acquire()
        self.targets.append(target)
        self.targetQueueLock.release()
    

    def load_html_message(self, filepath : str):

        with open(filepath, 'r', encoding='UTF-8') as message:
            
            message_content = message.read()
            message.close()

        self.message_raw = message_content


    def header(self, header : str, value : str):

        self.headers[header] = value


    def starttls(self):

        self.options['starttls'] = 'true'

    def launch_agents(self, num_agents=50):

        self.message.attach(MIMEText(self.message_raw, 'html'))

        for i in range(num_agents):

            agent = MailbombAgent(i, self.host, self.port, self.login, self.key, self)
            agent.start()
            self.agents.append(agent)

    
    def terminate(self):

        for agent in self.agents:

            agent.join()
            self.missed.extend(agent.missed_addresses)

        with open(self.log, 'w+', encoding='UTF-8') as f:

            f.writelines(self.missed)
            f.close()


class MailbombAgent(Thread):

    def __init__(self, id, host, port, login, key, mailbomb : Mailbomb):

        print("Starting agent #" + str(id) + "...")
        Thread.__init__(self)
        self.id = id
        self.host = host
        self.port = port
        self.login = login
        self.key = key
        self.s = None
        self.bomb = mailbomb
        self.connected = False
        self.missed_addresses = []
    
    def run(self):

        print("Running...")
        self.login_smtp_server()
        self.send_messages()
    

    def login_smtp_server(self):

        try:

            self.s = smtplib.SMTP(host=self.host, port=self.port)
            if self.bomb.options['starttls'] == 'true':
                self.s.starttls()
            self.s.login(user=self.login, password=self.key)
            self.connected = True

        except smtplib.SMTPServerDisconnected:

            print("Server stopped the connection in agent #" + str(self.id))


    def send_messages(self):

        while True:

            try:

                self.bomb.targetQueueLock.acquire()
                if len(self.bomb.targets) != 0 and self.connected:

                    queueFront = self.bomb.targets.pop(0)
                    self.bomb.targetQueueLock.release()
                
                else: 

                    self.bomb.targetQueueLock.release()
                    break

                message_raw = self.bomb.message_raw
                message = MIMEMultipart()
                message.attach(MIMEText(message_raw, 'html'))
                message.add_header('To', queueFront)

                for header, value in self.bomb.headers.items():

                    message.add_header(header, value)

                self.s.send_message(message)
                print("Sent message to " + queueFront + " using agent #" + str(self.id))

            except (smtplib.SMTPHeloError, smtplib.SMTPRecipientsRefused,
                smtplib.SMTPSenderRefused, smtplib.SMTPServerDisconnected, smtplib.SMTPDataError):
                
                self.missed_addresses.append(queueFront + "\n")
