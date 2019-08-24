import os
import time

import smtplib
from pathlib import Path

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import credentials
from .config import default_credentials


class Emailer:
    """Welcome to the auto-emailer to send all of your emails!"""
    def __init__(self, config=None, delay_login=True):
        """
        Args:
            config (Optional(config.credentials.Credentials)): The constructed
                credentials. Can be None if environment variables are
                configured.
            delay_login (bool): If True, no login attempt will be made until
                send_mail is called. Otherwise, a login attempt will be made at
                class initialization.

        Raises:
            ValueError: If config is not in the expected format.
            EnvironmentError: If default_credentials is called and environment
                variables are not found.
        """
        if (config is not None and
                not isinstance(config, credentials.Credentials)):
            raise ValueError('Emailer class only supports credentials from '
                             'auto_emailer.config. See '
                             'auto_emailer.config.credentials and '
                             'auto_emailer.config.environment_vars for help on '
                             'authentication with auto-emailer library.')
        elif config is None:
            try:
                self._config = default_credentials()
            except EnvironmentError:
                raise EnvironmentError('Emailer only supports credentials from '
                                       'auto_emailer.config. Either define and '
                                       'pass explicitly to Emailer() or set '
                                       'environment_vars.')
        else:
            self._config = config

        self._connected = False
        if not delay_login:
            self._login()

    @property
    def connected(self):
        """Return: bool: If SMTP client is logged in or not.
        """
        return self._connected

    def _logout(self):
        """Quits the connection to the smtp client."""
        if self.connected:
            try:
                self._smtp.quit()
            except smtplib.SMTPServerDisconnected:
                pass
        self._connected = False

    def _login(self):
        """Uses the class attribute Emailer._config to connect
        to SMTP client.
        """
        self._smtp = smtplib.SMTP(host=self._config.host,
                                  port=self._config.port)
        # send 'hello' to SMTP server
        self._smtp.ehlo()
        # start TLS encryption
        self._smtp.starttls()
        self._smtp.login(self._config.sender_email, self._config.password)
        self._connected = True

    def send_email(self, message, from_addr=None, to_addrs=None,
                   delay_send=0):
        """Send an email message through the SMTP client.

        The message may either be a string containing characters
        in the ASCII range, or an `auto_emailer.emailer.Message` object.

        If the message is a string, the smtplib delivery method will
        use `smtplib.sendmail`.

        If the message is an `auto_emailer.emailer.Message` object, the smtplib
        delivery method will use `smtplib.send_message`. The message is
        then converted to a bytestring and passes it to `smtplib.sendmail`.
        The arguments are the same as for sendmail, except that message is
        an `auto_emailer.emailer.Message` object. If from_addr is None or
        to_addrs is None, these arguments are taken from the headers of the
        message as described in RFC 2822 (a ValueError is raised if there is
        more than one set of 'Resent-' headers).

        Args:
            message (Union[auto_emailer.emailer.Message, str]): The message may
                either be a string containing characters in the ASCII
                range, or an `auto_emailer.emailer.Message` object.
            from_addr (Optional[str]): The address sending the mail.
            to_addrs (Optional(Sequence[str])): A list of addresses to
                send the email to. A bare string will be treated as a
                list with 1 address.
            delay_send (Optional[int]): If you would like to delay sending
                the email, pass in amount of time in seconds.

        Raises:
            ValueError: If sending a string email and from_addr or to_addr
                is None.
            ValueError: If the message is not an auto_emailer.emailer.Message
                object or a string.
        """
        if not isinstance(message, Message) and isinstance(message, str):
            smtp_meth = 'sendmail'
            if (from_addr is None) or (to_addrs is None):
                raise ValueError('If sending string email, please provide '
                                 'from_addr and to_addrs.')
        elif isinstance(message, Message):
            smtp_meth = 'send_message'
            message = message.message
        else:
            raise ValueError('The message argument must either be an '
                             'auto_emailer.emailer.Message object or a string.')

        # delay sending by input value
        if delay_send:
            time.sleep(delay_send)

        # log in to email client if not already
        if not self._connected:
            self._login()

        # handle disconnect and connection errors by
        # quick login and attempt to send again
        try:
            delivery_meth = getattr(self._smtp, smtp_meth)
            delivery_meth(msg=message, from_addr=from_addr,
                          to_addrs=to_addrs)
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
            self._login()
            # needs to call getattr() again once it hits
            # here otherwise it will fail
            delivery_meth = getattr(self._smtp, smtp_meth)
            delivery_meth(msg=message, from_addr=from_addr,
                          to_addrs=to_addrs)
        finally:
            self._logout()


class Message:
    """Class representing an email message."""
    def __init__(self, sender, destinations, subject=None, cc=None, bcc=None):
        """
        Args:
            sender (str): Email address of the sender (from).
            destinations (Sequence[str]): List of string email
                addresses to send the email message to.
            subject (Optional[str]): Subject of your email message.
            cc (Optional(Sequence[str])): List of string email
                addresses to CC the email message to.
            bcc (Optional(Sequence[str])): List of string email
                addresses to BCC on the email message.
        """
        self.sender = sender
        self.destinations = destinations
        self.subject = subject
        self.cc = cc or []
        self.bcc = bcc or []
        # create multi-part message
        self.message = MIMEMultipart()

    def __str__(self):
        """Override __str__ method to return message as string"""
        return self.message.as_string()

    @staticmethod
    def body_template(template_path):
        """Opens, reads, and returns the given template text file
        path as a string.

        Args:
            template_path (str): File path for the email template.

        Returns:
            str: Text of file.

        Raises:
            FileNotFoundError: If cannot find the file from given
                `template_path`.
        """
        try:
            template_text = Path(template_path).read_text()
        except FileNotFoundError:
            raise FileNotFoundError('File path not found: {}'
                                    .format(template_path))
        return template_text

    def draft_message(self, text=None, template_path=None, template_args=None):
        """Create, or draft, the `self.message` instance attribute with
        string text or text file templates. Return self from the instance
        to allow method chaining of `auto_emailer.emailer.Message.attach`.

        Args:
            text (Optional[str]): The body text of your email message.
            template_path (Optional[str]): File path of a text
                template to use for the email message body.
            template_args (Optional[dict]): Keyword arguments to format
                the email message template text.

        Returns:
            auto_emailer.emailer.Message: The instance of
            auto_emailer.emailer.Message.
        """
        self.message['From'] = self.sender
        self.message['To'] = '; '.join(self.destinations)
        self.message['BCC'] = '; '.join(self.bcc)
        self.message['CC'] = '; '.join(self.cc)
        self.message['Subject'] = self.subject

        # check if email template is used
        if template_path:
            text = self.body_template(template_path)
            text = text.format(**template_args)

        # attach text part of message
        self.message.attach(MIMEText(text))

        # return self to encourage method chaining
        return self

    def attach(self, attach_files=None):
        """Add a sequence of files as attachments to the
        email message.

        Args:
            attach_files (Optional(Sequence[str])): List of string file
                paths to attached to message.

        Returns:
            auto_emailer.emailer.Message: The instance of
            auto_emailer.emailer.Message.
        """
        # iterate through files to attach
        for path in attach_files or []:
            part = MIMEBase('application', "octet-stream")
            with open(path, 'rb') as file:
                part.set_payload(file.read())

            # encode file in ASCII characters to send by email
            encoders.encode_base64(part)
            # add header to attachment part
            part.add_header('Content-Disposition',
                            'attachment',
                            filename=os.path.basename(path))
            self.message.attach(part)

        return self
