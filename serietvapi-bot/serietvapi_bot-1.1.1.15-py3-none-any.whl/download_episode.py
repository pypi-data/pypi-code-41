# -*- coding: utf-8 -*-
from __future__ import unicode_literals # standard
from random import randint # standard
import youtube_dl, requests # da scaricare
import os, json, os.path, threading, string, random

class Downloader(threading.Thread):
	def __init__(self, bot):
		self.bot = bot
		self.files = []
		self.flag_error = False
		self.download_ua = {}
		threading.Thread.__init__(self)

	def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def run(self):
		try:
			headers = {'User-Agent': 'init/1.0'}
			NewUDA = self.id_generator()
			Update_UA = self.bot.execute_command(1, "private_update_value", "w", {'record': NewUDA, 'k':'fixed_security'}, headers)

			if Update_UA["ok"] == False:
				print(Update_UA["info"])
				self.flag_error = True
				rj = self.bot.execute_command(1, "tg_message", "r", {'msg':'<b>😵 Errore con le API</b>\n\nNon è stato possibile autorizzare il tuo account a causa di un errore interno.\n\nQuesto problema non influenza il tuo account API in quanto ha cause di natura interna tecnica, se possibile contatta @KingKaitoKid oppure lo staff del bot @SerieTvItaly_bot premendo /start e poi premere il pulsante Contattaci.'}, headers)
			else:
				headers = {'User-Agent': NewUDA}
				self.download_ua = headers
				JSON_infos = self.bot.execute_command(1, "download_episode", "r", {}, headers)
				#print(JSON_infos)
				if (JSON_infos["ok"] == False):
					if "reeason" in JSON_infos:
						print(JSON_infos["info"] + "\n\t" + JSON_infos["reeason"])
						reason = JSON_infos['reeason']
					else:
						print(JSON_infos["info"])
						reason = ""
					self.bot.execute_command(1, "tg_message", "r", {'msg':'<b>🙅‍♂️ Un errore col tuo account</b>\n\nÈ stato riscontrato un errore, ed è il seguente: ' + JSON_infos['info'] + " " + reason}, headers)
				else:
					SerieInfo_array = JSON_infos["info"]["episodi"]["info_episodio"]

					counter = 0
					file_names = []
					threads = []
					for single_SerieInfo in SerieInfo_array:
						Name_File = single_SerieInfo["openload_file_name"]
						Dimensioni = single_SerieInfo["dimensioni"]
						rj = self.bot.execute_command(1, "tg_message", "r", {'msg':'<b>📥 Download file in corso</b>\n\nIl file chiamato ' + Name_File + ' (' + Dimensioni + ') è in fase di download, il file rimarrà salvato fino a quando il caricamento non è completato.'}, headers)
						exec("%s = self.Openload_Down(\"%s\", \"%s\", %d, %d, %s, %s)" % ("YDL_OPEN_" + str(counter), single_SerieInfo["link_diretto"], Name_File, 0, single_SerieInfo["id_episodio"], "self.bot", headers))
						exec("%s.start()" % ("YDL_OPEN_" + str(counter)))
						exec("threads.append(%s)" % ("YDL_OPEN_" + str(counter)))
						print("Avvio download del file chiamato: " + Name_File + " (" + Dimensioni + ")")
						self.files.append(Name_File)
						counter += 1

					for t in threads: # aspettiam che finisce il download dei file
						t.join()
		except Exception as e:
			self.flag_error = True
			rj = self.bot.execute_command(1, "tg_message", "r", {'msg':'<b>🏴 Impossibile effettuare il download episodi</b>Il tuo account sembra essere OK ma a causa di un problema tecnico non è stato possible scaricare gli episodi della serie TV da te selezionata.\n\nQuesto problema è di natura interna, quindi è riconosciuto dal bot e non penalizza bloccandoti l\' account API, se il problema persiste contatta @KingKaitoKid oppure lo staff del bot @SerieTvItaly_bot facendo /start e poi premendo il pulsante Contattaci.'}, headers)

	class Openload_Down(threading.Thread):
		"""docstring for Openload_Down"""
		def __init__(self, link_downl, Name_File, ChatID, id_episodio, bot, headers):
			threading.Thread.__init__(self)
			self.single_link = link_downl
			self.from_id = ChatID
			self.fname = Name_File
			self.id_ep = id_episodio
			self.bot = bot
			self.h = headers

		def run(self):
			ydl_opts = {
				'format': '0',
				'quiet': True,
				'no_warnings': True,
				'nocheckcertificate': True,
				'outtmpl': self.fname,
			}

			try:
				with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					ydl.download([self.single_link])

				print("File " + self.fname + " scaricato con successo")
				from mutagen.mp4 import MP4
				mp4_video = MP4(self.fname)
				mp4_video["\xa9nam"] = [self.fname]
				mp4_video.save()
				rj = self.bot.execute_command(1, "tg_message", "r", {'msg':"<b>👍 Download file completato</b>\n\nIl file chiamato " + self.fname + " è stato scaricato sul tuo PC ed è stato rimosso."}, self.h)

			except Exception as e:
				rj = self.bot.execute_command(1, "tg_message", "r", {'msg':"<b>😓 Errore nelle API</b>\n\nC'è stato un errre nella integrazione API se è un errore frequente ti preghiamo di segnalarlo su GitHub nella sezione Issue al seguente link: https://github.com/KingKaitoKid/serietvapi_bot/issues oppure contattaci attraverso il bot @SerieTvItaly_bot descrivendo il problema."}, self.h)
				print("C'è stato un errore: " + str(e))
				exit()
