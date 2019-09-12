import datetime
import uuid


class MemoryDB(object):
    secret_table = {}

    def create_secret_entry(self, secret_data, wipe_data, expire_in_seconds, is_consumable):
        # Prevent duplicate entries:
        #    MemoryDB - Have to check if key exists first
        #    DynamoDB - Use put_item's attribute_not_exists
        #    Redis - Use SETNX (SET if Not eXists)
        # Basically attempt to insert, let the DB engine fail, retry until you get a successful insert with a new ID
        # Since we're using UUIDs this should literally never happen, but we don't EVER want to accidentally overwrite
        # existing good data. This method allows us to not take a check-before-write cycle and let the checking happen
        # during insert and only submitting two queries if we have to anyway.
        while True:
            secret_id = str(uuid.uuid4()).replace('-', '')
            if secret_id in self.secret_table:
                continue
            # MemoryDB stores the timestamp in the form of a date on which it expires.
            expiration = (datetime.datetime.now() + datetime.timedelta(seconds=expire_in_seconds))
            self.secret_table[secret_id] = {
                'id': secret_id,
                'secret': secret_data,
                'wipe': wipe_data,
                'expiration': expiration.timestamp(),
                'consumable': is_consumable

            }
            return secret_id

    def retrieve_secret_entry(self, secret_id):
        # If a secret exists, return it.
        # If a secret doesn't exist return a dummy secret that will fail to decrypt.
        #
        # Why do this? A potential attack vector could be to compare processing times to find a valid secret_id. A
        # valid id would normally require time (lookup + secret decrypt + wipe decrypt) before it is determined to be
        # wrong. An invalid id could just return 404 in a much shorter time. An attacker could attempt random ids until
        # it finds one that has a longer response time (since it actually tried to decrypt data) and then attempt to
        # determine a secret view key.
        #
        # The way written below we will return an value which will always fail to decrypt if not found. This means that
        # valid entries, invalid entries, and valid but expired entries should all take roughly the same amount of time
        # to verify. The data below was randomly generated and the key discarded.
        #
        # It is still possible that with a accurate and stable enough latency to the service that you could pick out
        # the processing time of the below entries. I think the only way to obfuscate the validity of entries further
        # would be to randomly select from a series of bad entries for decryption.
        if secret_id in self.secret_table:
            # The secret exists to retrieve it
            secret = self.secret_table[secret_id]
        else:
            # The secret doesn't exist so create a dummy one
            secret = {
                'id': secret_id,
                'secret': ('gAAAAABddtdvr6pSgtvGAsMVkH9aBvHlE1dFOH0UY1zcSlsFOYMxvzdCsTro'
                           'ma4iH2Qc2sU_mf2k9kpNGC7NQusw4tckpdmSYqgYexaRr4Bwe1rW9tFa98s='),
                'wipe': ('gAAAAABddtdv82xa6zoJwtgH0qmGCYtiqcCB6PNd8CozmTyYi6jQks5twksoYH1cbzxlG3'
                         'G5TePlkPEsiU8hymV-iPj1kcfz5tr0hUaHFUf8x6XWxRmrmxOh_m9HeCHyJO15SKqd50cz'),
                'expiration': 1568155243.205841,
                'consumable': False
            }
        # The secret (either real or dummy) should be checked for expiration
        if datetime.datetime.now() > datetime.datetime.fromtimestamp(secret['expiration']):
            # Expired so set a dummy secret
            secret = {
                'id': secret_id,
                'secret': ('gAAAAABddtdvr6pSgtvGAsMVkH9aBvHlE1dFOH0UY1zcSlsFOYMxvzdCsTro'
                           'ma4iH2Qc2sU_mf2k9kpNGC7NQusw4tckpdmSYqgYexaRr4Bwe1rW9tFa98s='),
                'wipe': ('gAAAAABddtdv82xa6zoJwtgH0qmGCYtiqcCB6PNd8CozmTyYi6jQks5twksoYH1cbzxlG3'
                         'G5TePlkPEsiU8hymV-iPj1kcfz5tr0hUaHFUf8x6XWxRmrmxOh_m9HeCHyJO15SKqd50cz'),
                'expiration': 1568155243.205841,
                'consumable': False
            }
        return secret

    def destroy_secret_entry(self, secret_id):
        if secret_id in self.secret_table:
            del self.secret_table[secret_id]
            return True
        else:
            return False
