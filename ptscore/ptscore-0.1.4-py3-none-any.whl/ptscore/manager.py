import uuid
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken


class Manager(object):
    database = None

    def __init__(self, database):
        self.database = database

    def create_secret(self, secret_plain, expire_in_seconds, is_consumable):
        # Set up the wipe plaintext
        wipe_plain = str(uuid.uuid4())
        # Get the encryption keys
        secret_key = Fernet.generate_key()
        wipe_key = Fernet.generate_key()
        # Set up the encryption objects with the keys
        secret_f = Fernet(secret_key)
        wipe_f = Fernet(wipe_key)
        # Get the encrypted data by encrypting it with key the user will be given
        secret_cipher = secret_f.encrypt(secret_plain.encode('UTF-8')).decode('UTF-8')
        wipe_cipher = wipe_f.encrypt(wipe_plain.encode('UTF-8')).decode('UTF-8')
        # Store the two tokens in the database with the secret_id as the Primary Key
        secret_id = self.database.create_secret_entry(secret_cipher, wipe_cipher, expire_in_seconds, is_consumable)
        secret_request_string = f"{secret_id}{secret_key.decode('UTF-8')}"
        wipe_request_string = f"{secret_id}{wipe_key.decode('UTF-8')}"
        return {
            'secret_request_string': secret_request_string,
            'wipe_request_string': wipe_request_string
        }

    def get_secret(self, request_string):
        if len(request_string) != 76:
            # Request Strings are always UUIDs without dashes (32 char) + Fernet Generated Key (44 char) = 76 char
            # Figure out how to articulate errors later
            raise ValueError('Malformed Request String')
        secret_id = request_string[:32]
        try:
            UUID(secret_id, version=4)
        except ValueError:
            # Not a valid UUID
            raise ValueError('Malformed Request String')
        encryption_key = request_string[32:]
        try:
            decrypt_f = Fernet(encryption_key)
        except ValueError:
            # Not a valid Fernet Key
            raise ValueError('Malformed Request String')
        secret_entry = self.database.retrieve_secret_entry(secret_id)
        # We're ALWAYS going to need to decrypt this one
        secret_entry['secret'] = secret_entry['secret'].encode('UTF-8')
        secret_decrypt_fail = False
        # Attempt to decrypt secret field
        try:
            plaintext = decrypt_f.decrypt(secret_entry['secret'])
        except InvalidToken:
            # If decrypting secret with user-provided key is unsuccessful then set flag to try to decrypt wipe
            secret_decrypt_fail = True
        if secret_decrypt_fail == False:
            # If decrypting secret with user-provider key is successful return it
            if not secret_entry['consumable']:
                # If not consumable then sent it to the user
                return {'secret': plaintext.decode('UTF-8')}
            else:
                # If consumable attempt a delete (before returning to user)
                destroy_successful = self.database.destroy_secret_entry(secret_id)
                if not destroy_successful:
                    # If not successful raise an error
                    raise LookupError('Not Found')
                else:
                    # If successful send it to the user, it has now been consumed
                    return {'secret': plaintext.decode('UTF-8')}
        # If decrypting secret with user-provided key is unsuccessful then attempt to decrypt wipe field
        try:
            plaintext = decrypt_f.decrypt(secret_entry['wipe'].encode('UTF-8'))
        except InvalidToken:
            # If decrypting wipe with user-provided key is unsuccessful then return not found.
            raise LookupError('Not Found')
        # If decrypting wipe with user-provider key is successful remove entry from the database
        if self.database.destroy_secret_entry(secret_id):
            return True
        else:
            # This should pretty much never happen. it means that we retrieved a secret entry, validated a wipe key and
            # then the secret was deleted before we requested it to be deleted. Either consumed or wiped by another
            # request while this request was in flight.
            raise LookupError('Not Found')
