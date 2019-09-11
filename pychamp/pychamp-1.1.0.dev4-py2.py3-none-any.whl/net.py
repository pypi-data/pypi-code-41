from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

hour = datetime.now().time().hour


class SendMail(object):
    def __init__(self, sender=None, host=None, password=None, port=None):
        self.sender = sender
        self.host = host
        self.password = password
        self.port = port

        try:

            if self.sender is None:
                self.sender = "noreply.extensodata@gmail.com"

            if self.host is None:
                self.host = 'smtp.gmail.com'

            if self.port is None:
                self.port = 587

            if self.password is None:
                self.password = "Khamsahammida977"

        except Exception as e:
            raise Exception(e)


    def send(self, receiver=[], bcc=[], cc=[], subject=None,
             message=None, attachment=None, salutation=None):
        self.receiver = receiver
        self.bcc = bcc
        self.cc = cc
        self.subject = subject
        self.message = message
        self.attachment = attachment
        self.salutation = salutation

        try:
            if self.receiver == []:
                raise Exception("Receiver email address must be provided!!")

            if self.subject is None:
                self.subject = "Test mail send."

            if self.message is None:
                self.message = "This is a test message."

            # instance of MIMEMultipart
            msg = MIMEMultipart()

            # storing the senders email address
            msg['From'] = self.sender
            if type(self.receiver) == list:
                msg['To'] = ", ".join(self.receiver)
            else:
                msg["To"] = self.receiver

            if len(cc) > 0:
                msg['Cc'] = ', '.join(self.cc)
            if len(bcc) > 0:
                msg['Bcc'] = ', '.join(self.bcc)

            # storing the subject
            msg['Subject'] = self.subject

            if self.salutation is None:
                if hour > 15:
                    self.salutation = "Good Evening!"
                elif hour > 11:
                    self.salutation = "Good Afternoon!"
                elif hour > 4:
                    self.salutation = "Good Morning!"
                else:
                    self.salutation = "Hello all!"

            body = """
                <html>
               <head></head>
               <body>
                  <p>{0}<br>
                     {1}
                  </p>
                  <br><br>
                  With regards,
                  <br><br>
                  <table  data-mysignature-date="2019-06-28T10:17:11.982Z" data-mysignature-is-paid="0" width="500" cellspacing="0" cellpadding="0" border="0">
                     <tr>
                        <td>
                           <table cellspacing="0" cellpadding="0" border="0">
                              <tr>
                                 <td style="font-size:1em;padding:0 15px 0 8px;vertical-align: top;" valign="top">
                                    <table cellspacing="0" cellpadding="0" border="0" style="line-height: 1.4;font-family:Verdana, Geneva, sans-serif;font-size:86%;color: #000001;">
                                       <tr>
                                          <td>
                                             <div style="font: 1.2em Verdana, Geneva, sans-serif;color:#000001;">Sagar Paudel</div>
                                          </td>
                                       </tr>
                                       <tr>
                                          <td style="padding: 4px 0;">
                                             <div style="color:#000001;font-family:Verdana, Geneva, sans-serif;"> Associated Data Scientist  |  Extensodata Pvt. Ltd.  |  Research and Development </div>
                                          </td>
                                       </tr>
                                       <tr>
                                          <td> <span style="font-family:Verdana, Geneva, sans-serif;color:#91AE6D;">mobile:&nbsp;</span> <span><a style="font-family:Verdana, Geneva, sans-serif;color:#000001;" href="tel:9845507636">9845507636</a></span> </td>
                                       </tr>
                                       <tr>
                                          <td> <span style="font-family:Verdana, Geneva, sans-serif;color:#91AE6D;">email:&nbsp;</span> <span><a href="mailto:sagar.poudel@extensodata.com" target="_blank" style="font-family:Verdana, Geneva, sans-serif;color: #000001;">sagar.poudel@extensodata.com</a></span> </td>
                                       </tr>
                                       <tr>
                                          <td> <span style="font-family:Verdana, Geneva, sans-serif;color:#91AE6D;">skype:&nbsp;</span> <span><a href="skype:sagar.paudel18@outlook.com?chat" style="font-family:Verdana, Geneva, sans-serif;color: #000001;">sagar.paudel18@outlook.com</a></span> </td>
                                       </tr>
                                       <tr>
                                          <td> <span style="font-family:Verdana, Geneva, sans-serif;color:#91AE6D;">address:&nbsp;</span> <span style="font-family:Verdana, Geneva, sans-serif;color:#000001;">Tukucha Marga, Naxal, Kathmandu</span> </td>
                                       </tr>
                                    </table>
                                 </td>
                                 <td style="border-left:3px solid;vertical-align:middle;padding:0 0 3px 6px;font-family: Arial;border-color:#91AE6D;" valign="middle">
                                    <table cellspacing="0" cellpadding="0" border="0" style="line-height: 1;">
                                       <tr>
                                          <td style="padding: 4px 0 0 0;"><a href="https://www.linkedin.com/in/sagar-paudel18/"><img alt="" style="width:22px;" width="22" src="https://img.mysignature.io/s/v3/0/d/a/0da47aae-d980-5ecc-919d-f6cbbc5bd6e2.png"></a></td>
                                       </tr>
                                       <tr>
                                          <td style="padding: 4px 0 0 0;"><a href="https://twitter.com/sagar_paudel18"><img alt="" style="width:22px;" width="22" src="https://img.mysignature.io/s/v3/3/b/0/3b046e7a-e788-5995-8cd3-a27b57e4dfa6.png"></a></td>
                                       </tr>
                                    </table>
                                 </td>
                              </tr>
                           </table>
                        </td>
                     </tr>
                  </table>
               </body>
            </html>
            """.format(self.salutation, self.message)

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(MIMEText(body, 'html'))

            if self.attachment is not None:
                # open the file to be sent
                if type(self.attachment) != list:
                    self.attachment = [self.attachment]

                for file in self.attachment:
                    filename = file
                    attachment = open(filename, "rb")

                    # instance of MIMEBase and named as p
                    p = MIMEBase('application', 'octet-stream')

                    # To change the payload into encoded form
                    p.set_payload((attachment).read())

                    # encode into base64
                    encoders.encode_base64(p)

                    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

                    # attach the instance 'p' to instance 'msg'
                    msg.attach(p)

            # creates SMTP session
            s = smtplib.SMTP(self.host, self.port)

            # start TLS for security
            s.starttls()

            # Authentication
            s.login(self.sender, self.password)

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail
            if len(self.cc) > 0 and len(self.bcc) > 0:
                s.sendmail(self.sender, (self.receiver+self.cc+self.bcc), text)
            elif len(cc) > 0:
                s.sendmail(self.sender, (self.receiver+self.cc), text)
            elif len(bcc) > 0:
                s.sendmail(self.sender, (self.receiver+self.bcc), text)
            else:
                s.sendmail(self.sender, self.receiver, text)

            print("\nEmail sent successfully.")
        except Exception as e:
            raise Exception(e)

if __name__ == "__main__":
    sm = SendMail()
    sm.send(receiver=["sagar.paudel18@gmail.com"], subject="Hi Sagar!")
