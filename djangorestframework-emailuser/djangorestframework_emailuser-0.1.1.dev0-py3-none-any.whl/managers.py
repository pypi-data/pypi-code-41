from django.contrib.auth.base_user import BaseUserManager


class EmailUserManager(BaseUserManager):

    def create_user(self, name, email, password=None):
        if not name:
            raise ValueError('Users must have a name.')
        if not email:
            raise ValueError('User must have an email.')
        user = self.model(name=name, email=self.normalize_email(email.lower()))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, name, email, password):
        if not password:
            raise ValueError('Superusers must have a password.')
        user = self.create_user(name, email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
    def get_by_natural_key(self, username):
        case_insensitive = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive: username})