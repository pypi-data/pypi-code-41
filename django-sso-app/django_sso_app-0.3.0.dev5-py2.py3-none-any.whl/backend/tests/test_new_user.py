from django.conf import settings

if settings.DJANGO_SSO_BACKEND_ENABLED:
    import time
    import os
    import re
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from django.core import mail
    from django.conf import settings

    from .base import TestFunzionale


    class NuovoVisitatoreTest(TestFunzionale):

        def test_puo_registrarsi_al_sito(self):
            step = 0
            # L'utente si connette all'indirizzo della pagina
            app_url = self.server_url + '?next=' + self.service.url
            self.browser.get(app_url)
            time.sleep(6)

            # riconosce la pagina
            self.identifica_titolo('Django SSO App')

            self.click_link('/login/')

            # che gli chiede di inserire le credenziali di accesso
            self.tag_contiene_testo('p', 'If you have not created an account yet, then please sign up first.')

            # prova a loggarsi
            self.compila_input_by_name('login', 'pippo@disney.com')

            self.compila_input_by_name('password', 'paperina')

            # vede che non è possibile senza creare un nuovo utente
            self.tag_contiene_testo('li', 'The e-mail address and/or password you specified are not correct.')

            # segue il link di registrazione
            self.click_link('/signup/')

            # inserisce email giusta
            self.compila_input_by_name('email', 'pippo@disney.com')

            # inserisce username
            self.compila_input_by_name('username', 'pippo')

            # inserisce password
            self.compila_input_by_name('password1', 'paperina')

            # conferma password
            self.compila_input_by_name('password2', 'paperina')

            # mette nome
            self.compila_input_by_name('first_name', 'Pippo')

            # mette cognome
            self.compila_input_by_name('last_name', 'Goofy')

            # mette description
            self.compila_input_by_name('description', 'Yuk! Yuk yuk yuk yuk!! YUK!', el="textarea")

            # inserisce immagine
            avatar_path = os.path.join(settings.ROOT_DIR, 'backend', 'tests', 'assets', 'avatar.png')
            self.browser.find_element_by_name('picture').send_keys(avatar_path)

            # inserisce posizione
            campo = self.compila_input_by_name('address', 'viale ettore andreis 74 desenzano', el="textarea")
            self.compila_input_by_name('latitude', '0')
            self.compila_input_by_name('longitude', '0')
            self.compila_input_by_name('country', 'it')

            # Lo si informa dell'avvenuta registrazione
            self.tag_contiene_testo('p', "We have sent an e-mail to you for verification. "
                                         "Follow the link provided to finalize the signup process. "
                                         "Please contact us if you do not receive it within a few minutes.")

            # Controlla la casella della posta in arrivo e segue il link di attivazione
            self.assertEqual(len(mail.outbox), 1)
            message = str(mail.outbox[0].message())
            print('MESSAGE!', message)
            activate_email_url = re.search("(?P<url>https?://.[^\s]+)", message).group("url")
            activate_email_url = activate_email_url.replace('http://' + settings.APP_DOMAIN, '')

            print('EMAIL_URL', activate_email_url, self.server_url + activate_email_url)
            self.browser.get(self.server_url + activate_email_url)

            time.sleep(1)

            # il link di attivazione lo redirige alla pagina di login
            self.tag_contiene_testo('p', 'If you have not created an account yet, then please sign up first.')

            # inserise le credenziali
            self.compila_input_by_name('login', 'pippo@disney.com')
            self.compila_input_by_name('password', 'paperina')

            time.sleep(2)

            self.tag_contiene_testo('h1', 'Welcome pippo')

            print('\n\nEOT')
            time.sleep(2)
