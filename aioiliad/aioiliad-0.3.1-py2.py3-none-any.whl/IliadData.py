"""IliadData module."""
import re
from datetime import datetime
from pytimeparse.timeparse import timeparse
from lxml import html
import aioiliad.xpaths


class IliadData(object):
    """Representation of IliadData."""

    def __init__(self, iliad):
        """Initialize Iliad Data."""
        self.iliad = iliad
        self.tree = html.fromstring(self.iliad.page)

    def get_general_info(self):
        """Get general info."""
        data = self._get_info(aioiliad.xpaths.GENERAL_INFO)
        data['id_utente'] = re.findall(r'\d+', data['id_utente'])[0]
        data['numero'] = ''.join(re.findall(r'\d+', data['numero']))
        data['rinnovo'] = datetime.strptime(
            re.findall(r'\d+/\d+/\d+', data['rinnovo'])[0], "%d/%m/%Y") \
            .timestamp()
        return data

    def get_italy(self):
        """Get italy info."""
        return self._get_consumption(aioiliad.xpaths.ITALIA)

    def get_estero(self):
        """Get abroad info."""
        data = self._get_consumption(aioiliad.xpaths.ESTERO)
        data['internet_over'] = re.findall(
            r'.+?(?= )', data['internet_over'])[0].strip()

        return data

    def _get_consumption(self, inputdata):
        """Get consumption info."""
        data = self._get_info(inputdata)

        data['sms_extra'] = re.sub(r'.*(extra): ', '', data['sms']).strip()
        data['sms'] = re.findall(r'.+?(?= SMS )', data['sms'])[0].strip()

        data['mms_extra'] = re.sub(r'.*(MMS): ', '', data['mms']).strip()
        data['mms'] = re.findall(r'.+?(?= MMS )', data['mms'])[0].strip()

        data['chiamate_extra'] = re.findall(
            r'(?<=voce: )(.*)', data['chiamate'])[0].strip()
        data['chiamate'] = timeparse(re.findall(
            r'(?<=Chiamate: )(.*)(?= Consumi)', data['chiamate'])[0].strip())

        data['internet_max'] = re.findall(
            r'(?<=\/ )[^ C]*', data['internet'])[0].strip()
        data['internet_over'] = re.findall(
            r'(?<=Dati: ).*$', data['internet'])[0].strip()
        data['internet'] = re.findall(
            r'.+?(?= \/ )', data['internet'])[0].strip()

        return data

    def _get_info(self, inputdata):
        """Get info."""
        result = {}
        for key in inputdata:
            res = self.tree.xpath(inputdata[key])
            if res:
                res_child_text = res[0].text_content()
                res_child_text_no_spaces = re.sub(r' +', ' ', res_child_text)
                res_child_text_no_spaces = re.sub(r'\r?\n', '',
                                                  res_child_text_no_spaces)
                res_child_text_no_spaces = re.sub(r' \t', '',
                                                  res_child_text_no_spaces)
                result[key] = res_child_text_no_spaces
        return result

    async def update(self):
        """Trigger update."""
        await self.iliad.update()
        self.tree = html.fromstring(self.iliad.page)
