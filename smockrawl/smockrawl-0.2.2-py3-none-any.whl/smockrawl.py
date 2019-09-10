#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import socket

import aiohttp
import async_timeout

from bs4 import BeautifulSoup
import dateutil.parser as dparser
from datetime import datetime
from humanfriendly.tables import format_pretty_table

import re

logger = logging.getLogger(__name__)


class Smockeo:
    """Holds state of a Smockeo smoke sensor."""

    URL_BASE = 'https://www.api.smockeo.com/'
    URLS = {'login': URL_BASE + 'login',
            'detector': URL_BASE + 'detector/index/{}',
            'incidents': URL_BASE + 'incidents/0/{}/0'}
    INCIDENT_SCOL_NAMES = ['Icon', 'Alert', 'Date']

    def __init__(self, username, password, id, loop, session):
        """Initialises the class."""
        self._loop = loop
        self._session = session
        self._last_poll = None
        self._logged_in = False
        self.login = {'username': username,
                      'password': password}
        self.sensor = {'id': id,
                       'name': None,
                       'building': None,
                       'address': None,
                       'status': None,
                       'status_message': None,
                       'last_update': None,
                       'last_test': None,
                       'battery_level': None,
                       'last_battery_change': None,
                       'signal_quality': None,
                       'serial': None,
                       'activation_date': None}
        self.incidents = {'last_five': None,
                          'all': None}

    def __repr__(self):
        """Representation for the Smockeo object."""
        return '<Smockeo sensor - ID: {}, authenticated: {}, polled: {}>'.format(self.sensor['id'],
                                                                                 self._logged_in,
                                                                                 self._last_poll)

    async def authenticate(self):
        """Logs in to the Smockeo API."""
        try:
            async with async_timeout.timeout(5, loop=self._loop):
                response = await self._session.post(
                    self.URLS['login'],
                    data={
                        'email': self.login['username'],
                        'password': self.login['password']},
                    allow_redirects=False)

            if response.status == 302:
                self._logged_in = True
            else:
                logger.error('Authentication failed. Status code: {}'.format(response.status))
                logger.debug('Content: {}'.format(await response.text()))
                raise AuthException('Authentication with Smockeo API failed. '
                                    'Status code: {}'.format(str(response.status)))

        except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror):
            raise ConnectionErrorException('Error loading data from Smockeo.')

    def auto_poll(self, activate=True):
        """Starts or stop scheduled polling."""
        raise NotImplementedError

    async def poll(self):
        """Polls the Smockeo API."""
        if self._logged_in:
            try:
                async with async_timeout.timeout(10, loop=self._loop):
                    response = await self._session.get(
                        self.URLS['detector'].format(self.sensor['id']))

                data = await response.text()
                self._last_poll = datetime.now()
                soup = BeautifulSoup(data, 'html.parser')
                self._parse(soup)

            except (asyncio.TimeoutError, aiohttp.ClientError, socket.gaierror):
                raise ConnectionErrorException('Error loading data from Smockeo.')
        else:
            raise NotAuthException('Authentication required before polling')
    
    def _parse(self, soup):
        """Parses the API response."""
        data1 = soup.select('#block-detector-information > .right-content > ul > li')
        data2 = soup.select('#block-detector-general > .right-content')
        data3 = data2[0].ul.select('li')
        data4 = soup.select('#block-detector-modify > .block-top > .right')
        data5 = soup.select('#block-incidents > table > tbody > tr')

        self.sensor['battery_level']        = data1[0].strong.span.string.split('%')[0]
        if '?' in self.sensor['battery_level']:
            self.sensor['battery_level'] = self.sensor['battery_level'][-3:].strip()
        battery_change_raw                  = data1[1].strong.next_sibling
        self.sensor['last_battery_change']  = dparser.parse(battery_change_raw, dayfirst=True, fuzzy=True)
        self.sensor['signal_quality']       = data1[2].strong.next_sibling.strip().split('%')[0]
        self.sensor['serial']               = data1[3].strong.next_sibling.strip()
        activation_raw                      = data1[4].strong.next_sibling
        self.sensor['activation_date']      = dparser.parse(activation_raw, dayfirst=True, fuzzy=True)

        self.sensor['status']               = data2[0].h4.string
        self.sensor['status_message']       = data2[0].p.string
        update_raw                          = data3[0].strong.next_sibling
        self.sensor['last_update']          = dparser.parse(update_raw, dayfirst=True, fuzzy=True)
        test_raw                            = data3[1].strong.next_sibling
        self.sensor['last_test']            = dparser.parse(test_raw, dayfirst=True, fuzzy=True)

        self.sensor['name']                 = data4[0].div.h5.text
        self.sensor['building']             = data4[0].div.h4.text
        self.sensor['address']              = re.sub('[\n+]', ', ', re.sub('[\t+]', '', data4[0].p.text.strip()))

        last_incidents = []
        for incident in data5:
            icon = incident.th.i['class'][1]
            data6 = incident.select('td')
            alert = data6[0].text
            # data6[1].text is the detector name, skipping.
            date = dparser.parse(data6[2].text, dayfirst=True, fuzzy=True)
            last_incidents.append([
                icon,
                alert,
                date
            ])
        self.incidents['last_five'] = last_incidents

    def _fetch_sensor_value(self, value):
        """Proxy function to return sensor values."""
        if self.last_poll is None:
            raise NotPolledException('Sensor value has been requested before API has been polled')
        else:
            return self.sensor[value]

    @property
    def last_poll(self):
        """Returns the time of the last API poll."""
        return self._last_poll

    @property
    def id(self):
        """Returns the ID of the sensor."""
        return self._fetch_sensor_value('id')

    @property
    def name(self):
        """Returns the name of the sensor."""
        return self._fetch_sensor_value('name')

    @property
    def building(self):
        """Returns the name of the building the sensor is located in."""
        return self._fetch_sensor_value('building')

    @property
    def address(self):
        """Returns the address of the building the sensor is located in."""
        return self._fetch_sensor_value('address')

    @property
    def status(self):
        """Returns the status of the sensor."""
        return self._fetch_sensor_value('status')

    @property
    def status_message(self):
        """Returns the status message of the sensor."""
        return self._fetch_sensor_value('status_message')

    @property
    def last_update(self):
        """Returns the time of the last status update of the sensor."""
        return self._fetch_sensor_value('last_update')

    @property
    def last_test(self):
        """Returns the time of the last test of the sensor."""
        return self._fetch_sensor_value('last_test')

    @property
    def battery_level(self):
        """Returns the battery level of the sensor in %."""
        return self._fetch_sensor_value('battery_level')

    @property
    def last_battery_change(self):
        """Returns the last time the sensor's battery was replaced."""
        return self._fetch_sensor_value('last_battery_change')

    @property
    def signal_quality(self):
        """Returns the signal quality of the sensor."""
        return self._fetch_sensor_value('signal_quality')

    @property
    def serial(self):
        """Returns the serial number of the sensor."""
        return self._fetch_sensor_value('serial')

    @property
    def activation_date(self):
        """Returns the activation date of the sensor."""
        return self._fetch_sensor_value('activation_date')

    def print_status(self):
        """Prints sensor information."""
        print('*** SMOCKEO SENSOR ID {} ***'.format(self.id))
        print('Name:                  {}'.format(self.name))
        print('Building:              {}'.format(self.building))
        print('Address:               {}'.format(self.address))
        print()
        print('Status:                {}'.format(self.status))
        print('Message:               {}'.format(self.status_message))
        print('Last update:           {}'.format(self.last_update))
        print('Last test:             {}'.format(self.last_test))
        print()
        print('Battery level:         {} %'.format(self.battery_level))
        print('Battery last changed:  {}'.format(self.last_battery_change))
        print('Signal level:          {} %'.format(self.signal_quality))
        print('Serial:                {}'.format(self.serial))
        print('Activation date:       {}'.format(self.activation_date))
        print()
        print('Latest incidents:')
        print(format_pretty_table(self.incidents['last_five'], self.INCIDENT_SCOL_NAMES))
        print()
        print('Last poll:             {}'.format(self.last_poll))


class AuthException(Exception):
    """Raised when there has been an authentication error."""

class NotAuthException(Exception):
    """Raised when API is polled before having been authenticated."""

class NotPolledException(Exception):
    """Raised when a sensor value is requested before API has been polled."""

class ConnectionErrorException(Exception):
    """Raised when there has been a connection error."""
