from django.db import models

from google.auth.transport.requests import Request
import pickle
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class GoogleAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='oauth_google')
    _creds = models.BinaryField()

    def set_data(self, data):
        self._creds = pickle.dumps(data)

    def get_data(self):
        credentials = pickle.loads(self._creds)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            self._creds = pickle.dumps(credentials)
            self.save()
        return pickle.loads(self._creds)

    creds = property(get_data, set_data)

    def __str__(self):
        return self.user.email


    class Meta:
        verbose_name = "Google Authentication"
        verbose_name_plural = "Google Authentications"

