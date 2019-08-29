from phovea_server.security import User, SecurityManager, ANONYMOUS_USER
from gevent.local import local

__author__ = 'Samuel Gratzl'


class CeleryUser(User):
  def __init__(self, id, roles):
    super(CeleryUser, self).__init__(id)
    self.name = id
    self.roles = roles

  @property
  def is_authenticated(self):
    return True

  @property
  def is_active(self):
    return True


class NotLoggedInException(Exception):
  pass


class CelerySecurityManager(SecurityManager):
  def __init__(self):
    super(CelerySecurityManager, self).__init__()
    self._context = local()

  def logout(self):
    delattr(self._context, 'user')

  def login(self, username, extra_fields=None):
    # cannot login in the ordinay way
    return None

  def login_celery(self, name, roles):
    user = CeleryUser(name, roles)
    self._context.user = user
    return user

  def login_required(self, f):
    import functools

    @functools.wraps(f)
    def check_required(*args, **kwargs):
      if not self.is_authenticated():
        raise NotLoggedInException('authenticated user is required to perform this action')
      return f(*args, **kwargs)

    return check_required

  @property
  def current_user(self):
    return getattr(self._context, 'user', ANONYMOUS_USER)


def create():
  return CelerySecurityManager()


def login_task(name, roles):
  from phovea_server.security import manager
  sec = manager()
  if isinstance(sec, CelerySecurityManager):
    sec.login_celery(name, roles)


def logout_task():
  from phovea_server.security import manager
  sec = manager()
  if isinstance(sec, CelerySecurityManager):
    sec.logout()
