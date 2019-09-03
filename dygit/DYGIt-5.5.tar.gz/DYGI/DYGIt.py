#!/usr/bin/env python
import npyscreen
import smtplib
import imaplib
import email
import json
import textwrap
import base64
import os
import sys
import curses
import datetime
from os.path import expanduser
from datetime import *
from httplib2 import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage
foldername = 'Inbox'
now = datetime.now()
home = expanduser("~/")
# how many days back you want to see your emails from.
body = "Data Unreadable"
conn = imaplib.IMAP4_SSL('imap.gmail.com', 993)
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.ehlo()
npyscreen.enableColor()
with open(home+ "/.DYGIdep/emailNum.txt", "w+") as f:
	if f.read() == '':
		f.write('100')
		numberOfEmails = 100
	else: 
		numberOfEmails = int(f.read())
f.close()
with open(home + "/.DYGIdep/Date.txt", "w+") as f:
	dateback = f.read()
	if f.read() == '':
		numberOfDaysBack = 7
		dateback = datetime.today()- timedelta(days=numberOfDaysBack)
		dateback = dateback.strftime('%d-%b-%Y')
		f.write(dateback)
		#dateback = datetime.strptime(dateback, '%d-%b-%Y')

f.close()
dta = None
retcode = ''
curses.initscr()
curses.start_color()
folderchange = False
gmail = ''
gmailpass = ''
def toLog(data):
	with open(home + "/.DYGIdep/log.txt", "a") as f:
		f.write("[" + str(datetime.today())+ "]: " + data + "\n")
		f.close()
toLog("----------START SESSION---------")
'''with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
	with open(home +"/.DYGIdep/folders.txt", "r") as x:
		line = x.readlines()
		#print "File deleted."
		toLog("Copied new folders.")
		x.close()
lastfolders.close()'''
line = []
colorList= ['DEFAULT',
    'FORMDEFAULT',
    'NO_EDIT',
    'STANDOUT',
    'CURSOR',
    'CURSOR_INVERSE',
    'LABEL',
    'LABELBOLD',
    'CONTROL',
    'IMPORTANT',
    'SAFE',
    'WARNING',
    'DANGER',
    'CRITICAL',
    'GOOD',
    'GOODHL',
    'VERYGOOD',
    'CAUTION',     
    'CAUTIONHL'] 
with open(home + "/.DYGIdep/currentFolder.txt", "w+") as f:
	foldername = f.read()
	if f.read() == '':
		f.write('Inbox')
class AppOne(npyscreen.NPSAppManaged):
	def onStart(self):
		with open(home +"/.DYGIdep/emails.txt", "w") as f:
			f.write("")
			toLog("Deleted contents of emails.txt")
			f.close()
		with open(home +"/.DYGIdep/ID.txt", "w") as x:
			x.write(str(""))
			toLog("Deleted contents of ID.txt")
			x.close()
		with open(home +"/.DYGIdep/results.txt", "w") as x:
			x.write(str(""))
			toLog("Deleted contents of results.txt")
			x.close()

		with open(home + '/.DYGIdep/color.txt', "r") as f:
			self.themeColor = f.read()
			self.themeColor = self.themeColor.replace("\n", "")
			toLog("Getting color palette from colors.txt")
		f.close()
		self.indexOfColor = colorList.index(self.themeColor)
		with open(home + "/.DYGIdep/DEBUG.txt", "w") as f:
			f.write(colorList[self.indexOfColor])
		f.close()
		self.addForm("MAIN", EmailClass, name="Login", color=colorList[self.indexOfColor])
		self.addForm("sendMail", SendMail, name="Write a Message", color=colorList[self.indexOfColor])
		self.addForm("Inbox", Inbox, name="Mail", color=colorList[self.indexOfColor])
		self.addForm("View", View, name="View Message",color=colorList[self.indexOfColor])
		self.addForm("changeFolder", changeFolder, name="Changing Folders", color=colorList[self.indexOfColor])
		self.addForm("changeTheme", changeTheme, name="Change The Theme", color=colorList[self.indexOfColor])
		self.addForm("changeDate", changeDate, name="Change Date", color=colorList[self.indexOfColor])
		self.addForm("buttonReply", replyButton, name="Reply", color=colorList[self.indexOfColor])
		toLog("Created Forms...")
class EmailClass(npyscreen.ActionForm):
	def activate(self):
		self.edit()
#		self.parentApp.setNextForm("sendMail")
	def create(self):
		global gmailpass
		global gmail
		gmail = self.add(npyscreen.TitleText, name="Gmail:")
		gmailpass = self.add(npyscreen.TitlePassword, name="Password:")
	def on_cancel(self):	
		toLog("----------END SESSION---------\n")		
		self.parentApp.switchForm(None)
	def on_ok(self):
		global line
		global IDoMessage
		try:
			conn.login(gmail.value, gmailpass.value)
			#GET EMAIL FOLDERS
			with open(home+"/.DYGIdep/folders.txt", "w") as folders:
				for i in conn.list()[1]:
					l = i.decode().split(' "/" ')
					folders.write(str(l[1]) + "\n")
			folders.close()
			toLog("Wrote new folders to folders.txt")

				#print(l)
				#print(l[0] + " = " + l[1])
			with open(home + ".DYGIdep/DEBUG.txt", "w") as debugger:
			#folderRead = open(home + "/.DYGIdep/folders.txt","r")
			#x = folderRead.readlines()
				with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
					with open(home +"/.DYGIdep/folders.txt", "r") as x:
						for l in x.readlines():
							lastfolders.writelines(l)
						x.close()
				lastfolders.close()
				with open(home+"/.DYGIdep/folders.txt", "r") as folders:
					#debugger.write(str(folders.read().splitlines()))
					#print(str(folders.read().splitlines()))
					global line
					line = folders.read().splitlines()
					#print line
					#self.m2 = self.add_menu(name="Folders", shortcut='f')
					#for x in folders.readlines():
					#self.m2.addItemsFromList([(line, self.changeFolder)])
				folders.close()
			#debugger.write(str(folderLines)
			#self.folders.addItemsFromList(folderLines)global foldername
			#global foldername
			debugger.close()
			foldername = 'Inbox'
			#	print foldername
			with open(home + "/.DYGIdep/DEBUG.txt", "w") as fd:
				foldername = foldername.replace("\n", "").replace("'", '"')
				stat, cnt = conn.select(foldername)
				#fd.write(foldername)
				fd.close()
			with open(home+ "/.DYGIdep/emailNum.txt", "r") as f:
				numberOfEmails = int(f.read())
			f.close()
			rv, data = conn.search(None, "(SINCE \""+ str(dateback) +"\")")
			count = 0
			npyscreen.notify("We are logging you in.  This may take a moment...", title="Logging In")
			with open(home +"/.DYGIdep/email.txt", "w") as f:
				with open(home +"/.DYGIdep/ID.txt", "w") as ids:
					for num in data[0].split():
						count += 1
						rv, data = conn.fetch(num, '(RFC822)')
						msg = email.message_from_string(data[0][1])
						dta = "[" + str(num) + "]" + msg['From'].replace("\n", "") + "\n"
						IDoMessage = msg['message-id']
						ids.write(IDoMessage + "\n")		
					#stat, dta = conn.fetch(cnt[0], '(BODY[HEADER.FIELDS (FROM)])')
						f.write(dta)
						if count >= numberOfEmails:
							break
				ids.close()

			f.close()
		
			#	(retcode, messages) = conn.search(None, '(UNSEEN)')
			server.login(gmail.value, gmailpass.value)
			global folderchange
			folderchange = True
			toSend = self.parentApp.getForm("Inbox")
			self.parentApp.switchForm("Inbox")
			self.parentApp.setNextFormPrevious("sendMail")
		except imaplib.IMAP4.error as e:
			toLog(str(e))
			npyscreen.notify_wait("Authentification Failed.  Try again or use a different account.", title="Error")
			self.parentApp.switchForm("MAIN")
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def on_cancel(self):
		self.parentApp.setNextForm("Inbox")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")
class replyButton(npyscreen.ActionForm, npyscreen.FormWithMenus):
	def create(self):
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
		self.menu.addItem("Change Date", self.cDate, "6")
		global message2
		message2 = self.add(npyscreen.MultiLineEdit, value="Type message contents here...")
		
	def on_ok(self):
		rv, data = conn.search(None, '(HEADER Message-ID "%s")' % searchtool.replace("\n", ""))
		num = data[0].split()
		rv, data = conn.fetch(num[0], '(RFC822)')
		original = email.message_from_string(data[0][1])
		with open(home + "/.DYGIdep/DEBUG.txt", "w") as f:
			f.write(str(original))
		f.close()
		new = MIMEMultipart("mixed")
		body = MIMEMultipart("alternative")
		body.attach( MIMEText(message2.value, "plain", "utf-8") )
		new.attach(body)
		new["Message-ID"] = email.utils.make_msgid()
		new["In-Reply-To"] = original["Message-ID"]
		new["References"] = original["Message-ID"]
		if new["Subject"] == None:
		    new["Subject"] == "Re: No Subject"
		else:
		    new["Subject"] = "Re: "+ original["Subject"]
		new["To"] = original["Reply-To"] or original["From"]
		new["From"] = gmail.value
		new.attach( MIMEMessage(original) )
		server.sendmail(gmail.value, [new["To"]], new.as_string())
		npyscreen.notify_confirm("Your message has been sent successfully!", title= 'Sent')
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		toLog("Logout")
		toLog("----------END SESSION---------\n")
		self.parentApp.switchForm(None)
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def on_cancel(self):
		self.parentApp.setNextForm("Inbox")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def cDate(self):
		toLog("Switching to changeDate form")
		self.parentApp.switchForm("changeDate")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")
class changeDate(npyscreen.ActionForm, npyscreen.FormWithMenus):
	def create(self):		
		self.explanation = self.add(npyscreen.TitleText, name="Use this to change how far back the program will look for emails.")
		self.CAUTIONT = self.add(npyscreen.TitleText, name="CAUTION: THE MORE EMAILS YOU LOAD THE LONGER IT WILL TAKE TO LOAD THEM", color="DANGER")
		self.numberOfEmails = self.add(npyscreen.Slider, label=True, name="Number of emails to display: ", lowest=0, step=10, out_of=100000)		
		self.dateChange = self.add(npyscreen.TitleDateCombo, name="Select Date Here: ", allowPastDate=True, allowTodaysDate=True)
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
	def on_ok(self):

		numberOfEmails = int(self.numberOfEmails.value)
		with open(home + "/.DYGIdep/emailNum.txt", "w") as f:
			f.write(str(numberOfEmails))
		f.close()
		with open(home + "/.DYGIdep/Date.txt", "w") as f:		
			if self.dateChange.value == '':
				numberOfDaysBack = 7
				dateback = datetime.today()- timedelta(days=numberOfDaysBack)
				dateback = dateback.strftime('%d-%b-%Y')
				f.write(dateback)
			else:
				dateback = self.dateChange.value
				toLog("date changed to " + str(dateback))
				if type(dateback) is str:
					dateback = datetime.strptime(dateback, '%d-%b-%Y')
				elif type(dateback) is not str:
					dateback = dateback.strftime('%d-%b-%Y')
				f.write(str(dateback))
		f.close()
		self.parentApp.switchForm("changeFolder")
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		toLog("Logout")
		toLog("----------END SESSION---------\n")
		self.parentApp.switchForm(None)
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def on_cancel(self):
		self.parentApp.setNextForm("Inbox")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")


class changeTheme(npyscreen.ActionForm, npyscreen.FormWithMenus):
	def create(self):
		self.colorListForm = self.add(npyscreen.SelectOne, values=[], name="Colors")	
		self.colorListForm.values = colorList
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
		self.menu.addItem("Change Date", self.cDate, "6")

	def on_ok(self):
		themeColor = self.colorListForm.values[self.colorListForm.value[0]]
		with open(home + '/.DYGIdep/color.txt', "w") as f:
			f.write(themeColor)
		f.close()
		npyscreen.notify_confirm("Color palette chosen.  Please restart DYGIt to change the color palette.")
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		toLog("Logout")
		toLog("----------END SESSION---------\n")
		self.parentApp.switchForm(None)
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def on_cancel(self):
		self.parentApp.setNextForm("Inbox")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def cDate(self):
		toLog("Switching to changeDate form")
		self.parentApp.switchForm("changeDate")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")
class changeFolder(npyscreen.ActionForm, npyscreen.FormWithMenus):
	def beforeEditing(self):
		if self.runOnce == 0:
			with open(home +"/.DYGIdep/folders.txt", "r") as f:
				global line
				line = f.readlines()
				toLog("Read lines from folders.txt")
			f.close()
			for x in line:
				self.listOfFolders.append(x)
			self.runOnce += 1

	def create(self):
		self.runOnce = 0
		toLog("Creating folder list...")
		self.folderList = self.add(npyscreen.SelectOne, values=[], name="Folders")	
		self.listOfFolders = []	
		self.folderList.values = self.listOfFolders
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
		self.menu.addItem("Change Date", self.cDate, "6")
		toLog("Folder list created.")
		
	def on_ok(self):
		selectedFolder = self.folderList.values[self.folderList.value[0]]
		#global foldername
		foldername = selectedFolder
		foldername = foldername.replace("\n", "").replace("'", '"')
		toLog("Changing Folders...")
		with open(home + ".DYGIdep/currentFolder.txt", "w") as f:
			f.write(str(foldername))
			toLog("Writing data to currentFolder.txt")

		server.login(gmail.value, gmailpass.value)
		with open(home + "/.DYGIdep/currentFolder.txt", "r") as f:
			toLog("Reading data from currentFolder.txt")
			foldername = f.read()
		#	print foldername
		with open(home + "/.DYGIdep/DEBUG.txt", "w") as fd:
			foldername = foldername.replace("\n", "").replace("'", '"')
			stat, cnt = conn.select(foldername)
			#fd.write(foldername)
			fd.close()
		with open(home + "/.DYGIdep/Date.txt", "r") as f:
			dateback = f.read()
		f.close()
		with open(home+ "/.DYGIdep/emailNum.txt", "r") as f:
			numberOfEmails = int(f.read())
		f.close()
		rv, data = conn.search(None, "(SINCE \""+ str(dateback) +"\")")
		count = 0
		npyscreen.notify("Changing Folders.  This may take a while depending on how many emails are in the folder...", title="Changing Folders")
		with open(home +"/.DYGIdep/email.txt", "w") as f:
			with open(home +"/.DYGIdep/ID.txt", "w") as ids:
				for num in data[0].split():
					count += 1
					rv, data = conn.fetch(num, '(RFC822)')
					msg = email.message_from_string(data[0][1])
					dta = "[" + str(num) + "]" + msg['From'].replace("\n", "") + "\n"
					IDoMessage = msg['message-id']
					ids.write(IDoMessage + "\n")		
				#stat, dta = conn.fetch(cnt[0], '(BODY[HEADER.FIELDS (FROM)])')
					f.write(dta)
					if count >= numberOfEmails:
						break
			ids.close()

		f.close()
	
		#	(retcode, messages) = conn.search(None, '(UNSEEN)')
		server.login(gmail.value, gmailpass.value)
		toLog("Folder changed.")
		toSend = self.parentApp.getForm("Inbox")
		self.parentApp.switchForm("Inbox")
		self.parentApp.setNextFormPrevious("SendMail")
		pass
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		toLog("Logout")
		toLog("----------END SESSION---------\n")
		self.parentApp.switchForm(None)
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def on_cancel(self):
		self.parentApp.setNextForm("Inbox")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def cDate(self):
		toLog("Switching to changeDate form")
		self.parentApp.switchForm("changeDate")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")
class View(npyscreen.ActionForm, npyscreen.FormWithMenus):
	def activate(self):
		lines = [line.rstrip('\n') for line in open(home +'/.DYGIdep/results.txt')]
		toLog("Getting email contents...")
		#lines = textwrap.wrap(str(lines), width=50)
		self.textLabel.values = lines
		self.textLabel.autowrap= True
		self.edit()
	def create(self):
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
		self.menu.addItem("Change Date", self.cDate, "6")
		self.menu.addItem("Reply", self.rep, "7")
		self.textLabel = self.add(npyscreen.Pager, values="\n", name="Email")
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		toLog("Logout")
		toLog("----------END SESSION---------\n")
		self.parentApp.switchForm(None)
	def rep(self):
		toLog("Sending to reply form")
		self.parentApp.switchForm("buttonReply")
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def on_cancel(self):
		self.parentApp.setNextForm("Inbox")
	def on_ok(self):
		self.parentApp.switchForm("View")
	def reply(self):
		self.parentApp.switchForm("Reply")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def cDate(self):
		toLog("Switching to changeDate form")
		self.parentApp.switchForm("changeDate")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")
class Inbox(npyscreen.ActionForm, npyscreen.FormWithMenus):
	#global line
	def activate(self):
		lines = [line.rstrip('\n') for line in open(home+'/.DYGIdep/email.txt')]
		self.selectMail.values = lines
		#self.Box.values = self.selectMail
		self.edit()
		#lines = str(lines).replace("'", '"')
	def create(self):
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
		self.menu.addItem("Change Date", self.cDate, "6")
		#self.folders = self.menu.addNewSubmenu("Email Folders")
	#self.Box = self.add(npyscreen.BoxTitle, name="Emails", max_width=60, max_height=50)
		self.selectMail = self.add(npyscreen.SelectOne, values=[])
			#self.add(npyscreen.TitleSelectOne, value=lines, name="Select an Email")
		
		#self.m2 = self.add(npyscreen.SelectOne, values=[])
		#foldername = self.m2.value
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		self.parentApp.switchForm(None)
		if os.name == 'nt':
			toLog("Logout")
			toLog("----------END SESSION---------\n")
			try:
				os.system('cls')
			except AttributeError:
				print "Program closed."
		else:
			toLog("Logout")
			toLog("----------END SESSION---------\n")			
			os.system('clear')
			print "Program closed."

	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def cDate(self):
		toLog("Switching to changeDate form")
		self.parentApp.switchForm("changeDate")
	def on_ok(self):
		global searchtool
		x = self.selectMail.values[self.selectMail.value[0]]
		with open(home +"/.DYGIdep/ID.txt", "r") as L:
			resultLines = L.readlines()
			L.close()
		searchtool = resultLines[self.selectMail.value[0]]
		searchtool = searchtool[1:]
		searchtool = searchtool.replace(">", "")
		#with open(home +"/.DYGIdep/DEBUG.txt", "w") as D:
			#D.write('(HEADER Message-ID "%s")' % searchtool.replace("\n", ""))

		#	D.close()
		with open(home + "/.DYGIdep/currentFolder.txt", "r") as f:
			foldername = f.read()
		stat, cnt = conn.select(foldername)
		#conn.mailbox(:all).find(gm: "rfc822msgid:#" + searchtool).first
		rv, data = conn.search(None, '(HEADER Message-ID "%s")' % searchtool.replace("\n", ""))
		#print data 
		with open(home +"/.DYGIdep/results.txt", "w") as f:
			#f.write(str(data))
			for num in data[0].split():
				rv, data = conn.fetch(num, '(RFC822)')
				raw_email = data[0][1]
				raw_email_string = raw_email.decode('utf-8')
				msg = email.message_from_string(raw_email)
				body = "Sorry, This content cannot be read through this program."
				for part in msg.walk():
					if part.get_content_type() == "text/plain":
						body = part.get_payload(decode=True)
				dta = str(body) + "\n"	
				if dta == "":
					f.write("No data")
				else:
					#stat, dta = conn.fetch(cnt[0], '(BODY[HEADER.FIELDS (FROM)])')
					f.write(dta)
				f.close()
		self.parentApp.switchForm("View")

	def on_cancel(self):
		self.parentApp.switchForm(None)

class SendMail(npyscreen.ActionForm, npyscreen.FormWithMenus):
	def create(self):
		global To
		global sub
		global message
		To = self.add(npyscreen.TitleText, name="To:")
		sub = self.add(npyscreen.TitleText, name="Subject:")
		message = self.add(npyscreen.MultiLineEdit, value="Type message contents here...")
		self.menu = self.new_menu(name="Selection Menu", shortcut='m')
		self.menu.addItem("Logout", self.logout, "1")
		self.menu.addItem("Send an Email", self.sendy, "2")
		self.menu.addItem("View Inbox", self.vInbox, "3")
		self.menu.addItem("Folders", self.changeFolder, "4")
		self.menu.addItem("Colors", self.changeColorP, "5")
		self.menu.addItem("Change Date", self.cDate, "6")
	def on_cancel(self):
		self.parentApp.switchFormPrevious()
	def on_ok(self):
		fmessage = 'Subject: {}\n\n{}'.format(sub.value, message.value)
		server.sendmail(gmail.value, To.value, fmessage)
		npyscreen.notify_confirm("Your message has been sent successfully!", title= 'Sent')
	def logout(self):
		conn.logout()
		with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
			with open(home +"/.DYGIdep/folders.txt", "r") as x:
				for l in x.readlines():
					lastfolders.writelines(l)
				#print "File deleted."
				toLog("Copied new folders.")
				x.close()
			'''with open(home +"/.DYGIdep/folders.txt", "w") as x:
				x.write(str(""))
				x.close()'''
		lastfolders.close()
		self.parentApp.switchForm(None)
		if os.name == 'nt':
			try:
				os.system('cls')
			except AttributeError:
				print "Program closed."
		else:			
			os.system('clear')
			print "Program closed."
	def sendy(self):
		toLog("Switching to send mail form")
		self.parentApp.switchForm("sendMail")
	def vInbox(self):
		toLog("Switching to inbox form ")
		self.parentApp.switchForm("Inbox")
	def changeFolder(self):
		self.parentApp.switchForm("changeFolder")
	def cDate(self):
		toLog("Switching to changeDate form")
		self.parentApp.switchForm("changeDate")
	def changeColorP(self):
		toLog("Switching to theme picker form.")
		self.parentApp.switchForm("changeTheme")



	

    
try:
	if __name__ == "__main__": 
	 	npyscreen.wrapper(AppOne().run())


except KeyboardInterrupt:
	toLog("Keyboard Interrupt")
	with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
		with open(home +"/.DYGIdep/folders.txt", "r") as x:
			for l in x.readlines():
				lastfolders.writelines(l)
			#print "File deleted."
			toLog("Copied new folders.")
			x.close()
		'''
		with open(home +"/.DYGIdep/folders.txt", "w") as x:
									x.write(str(""))
									x.close()
		'''
	lastfolders.close()
	toLog("----------END SESSION---------\n")
	sys.exit()	
except SystemExit:
	with open(home + "/.DYGIdep/lastfolders.txt", "w") as lastfolders:
		with open(home +"/.DYGIdep/folders.txt", "r") as x:
			for l in x.readlines():
				lastfolders.writelines(l)
			#print "File deleted."
			toLog("Copied new folders.")
			x.close()
		'''
		with open(home +"/.DYGIdep/folders.txt", "w") as x:
									x.write(str(""))
									x.close()
		'''
	lastfolders.close()
	toLog("----------END SESSION---------\n")
	sys.exit()	
except AttributeError as e:
	toLog(str(e))
	print "Program Terminated"
