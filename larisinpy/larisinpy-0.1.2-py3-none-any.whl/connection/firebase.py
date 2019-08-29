#%%
import firebase_admin
import os.path
import pandas as pd

from datetime import datetime
from firebase_admin import credentials, auth, _utils
from firebase_admin.db import reference, Reference, _DatabaseService

_DB_ATTRIBUTE = '_database'

#%%
class FirebaseUtils(object):

    def __init__(self, CREDENTIALS_PATH=None, DB_URL=None):

        self.FIREBASE_CREDENTIALS_PATH = CREDENTIALS_PATH
        self.FIREBASE_DATABASE_URL = DB_URL

    def connect(self):
        """Initializes and returns a new App instance.

        Returns:
            app firebase instance connection.
        """
        # Check credentials service account is exist
        if not os.path.exists(self.FIREBASE_CREDENTIALS_PATH):
            return ValueError("FIREBASE_CREDENTIALS_PATH is not found.")

        # Fetch the service account key JSON file contents
        cred = credentials.Certificate(self.FIREBASE_CREDENTIALS_PATH)
        
        # Initialize the app with a service account, 
        # granting admin privileges
        app = firebase_admin.initialize_app(
                cred, {'databaseURL': self.FIREBASE_DATABASE_URL})

        print("Connected to Firebase DB : {}".format(
                self.FIREBASE_DATABASE_URL))
            
        return app

    def disconnect(self, app):
        """Delete firebase connection

        Args:
            app : App instance
        Returns:
            Deleted connection
        """
        return firebase_admin.delete_app(app)

class FirebaseRealtime(FirebaseUtils):

    def reference(self, path='/', app=None, url=None):
        
        service = _utils.get_app_service(app, _DB_ATTRIBUTE, _DatabaseService)
        client = service.get_client(url)
        return Reference(client=client, path=path)

    def get(self):
        return Reference().get(etag=False, shallow=False)

    def set(self, value):
        return Reference().set(value)

    def update(self, value):
        return Reference().update(value)

#%%
class FirebaseAuth(FirebaseUtils):

    def get_auth_list(self):
        """ Iterate through all users

            Iterate through all users. This will still retrieve users in batches,
            buffering no more than 1000 users in memory at a time.

            Imported as dataframe
        """

        def dt_from_ms(ms):
            """ Convert miliseconds to UTC 

            """
            try:
                date = str(datetime.utcfromtimestamp(ms / 1000.0)).replace(
                            " ", "T")[:23]+"Z"
            except:
                date = "0000-00-00T00:00:00.000Z"
            return date

        user_auth_col = [
            "user_id", "user_email", "user_phone", "disabled", "created_at", 
            "last_sign_in"
        ]

        user_auth_matrix = []
        for user in auth.list_users().iterate_all():

            row = [
                user.uid,
                user.email,
                user.phone_number,
                user.disabled,
                user.user_metadata.creation_timestamp,
                user.user_metadata.last_sign_in_timestamp
            ]

            user_auth_matrix.append(row)
            
        auth_df = pd.DataFrame(user_auth_matrix, 
                               columns=user_auth_col
                    )
        auth_df["created_at"] = auth_df["created_at"].apply(
            lambda x: dt_from_ms(x))
        auth_df["last_sign_in"] = auth_df["last_sign_in"].apply(
            lambda x: dt_from_ms(x))

        return auth_df