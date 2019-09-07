from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from ps_herald import db, login
from ps.Basic import Basic


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)



class Log(db.Model):
 """The model currently is build around the data structure, the standard python logging mechanism
   uses to send logging Events across the **class logging.StreamHandler()**.
 """
 __tablename__ = 'log'
 __table_args__ = {'sqlite_autoincrement': True} # needed for sqlite. needed for pg ?
 id                = db.Column(db.Integer,primary_key=True)
 created           = db.Column(db.String())     #:e.g. 2015-01-08 10:52:41 currently the time the record is created in the
                                                #bridge as string sqlite does not support datetime per se here, that is, why the
                                                #string representation was choosen.
 threadname        = db.Column(db.String())     #:e.g. MainThread
 api_version       = db.Column(db.String())     #:e.g. 1.2.44
 package_version   = db.Column(db.String())     #:e.g. The version of the module where logging appeared
 name              = db.Column(db.String())     #:e.g. Tests
 relativecreated   = db.Column(db.Float())      #:e.g. 10.5919839592
 process           = db.Column(db.Integer)      #:e.g. 896
 args              = db.Column(db.String())     #:e.g. None
 module            = db.Column(db.String())     #:e.g. t
 funcname          = db.Column(db.String())     #:e.g. run
 levelno           = db.Column(db.Integer)      #:e.g. 40
 processname       = db.Column(db.String())     #:MainProcess
 thread            = db.Column(db.BigInteger)   #:e.g. 140735286908888
 msecs             = db.Column(db.Float())      #:e.g. 616.5919839592
 message           = db.Column(db.String())     #:e.g. "The msg of a log.info statement"
 exc_text          = db.Column(db.String())     #:e.g. None
 exc_info          = db.Column(db.String())     #:e.g. None
 stack_info        = db.Column(db.String())     #:e.g. None
 pathname          = db.Column(db.String())     #:e.g. /Users/setzt/Haufe/basic_package
 filename          = db.Column(db.String())     #:e.g. Basic.py
 asctime           = db.Column(db.String())     #:e.g. ????
 levelname         = db.Column(db.String())     #:INFO
 lineno            = db.Column(db.Integer)      #:e.g. 42
 # These are "extra fields" not in the standard python logging
 produkt_id        = db.Column(db.String(10))   #:e.g. PRODUKT_ID
 system_id         = db.Column(db.String(10))   #:e.g. SYSTEM_ID
 sub_system_id     = db.Column(db.String(10))   #:e.g. SUB_SYSTEM_ID
 sub_sub_system_id = db.Column(db.String(10))   #:e.g. SUB_SUB_SYSTEM_ID
 user_spec_1       = db.Column(db.String(10))   #:e.g. User_specific_value_one
 user_spec_2       = db.Column(db.String(10))   #:e.g. User_specific_value_two
 summary           = db.Column(db.String(70))   #:e.g. concatenation of the before values






 def __repr__(self):
  d={}
  d['created']             = self.created
  d['package_version']     = self.package_version
  d['module']              = self.module
  d['lineno']              = self.lineno
  d['funcname']            = self.funcname
  try:    d['lower_levelname']     = self.levelname.lower()
  except: d['lower_levelname']     = str(self.levelno)

  d['levelname']           = self.levelname
  d['message']             = self.message
  d['exc_text']            = self.exc_text
  d['stack_info']          = self.stack_info
  d['system_id']           = self.system_id
  d['sub_system_id']       = self.sub_system_id
  d['sub_sub_system_id']   = self.sub_sub_system_id
  d['user_spec_1']         = self.user_spec_1
  d['user_spec_2']         = self.user_spec_2
  d['produkt_id']          = self.produkt_id

  return '<tr class="%(lower_levelname)s"> \
                           <td>%(created)s</td> \
                           <td>%(levelname)s</td> \
                           <td>%(system_id)s<br>%(sub_system_id)s<br>%(sub_sub_system_id)s</td> \
                           <td>%(produkt_id)s<br>%(user_spec_1)s<br>%(user_spec_2)s</td>\
                           <td>%(module)s %(package_version)s<br>%(funcname)s<br>line: %(lineno)s<br></td> \
                           <td>%(message)s</td> \
                           <td>%(exc_text)s</td> \
                           <td>%(stack_info)s</td> \
                           </tr>'%d




class HeartBeat(db.Model):
 """Store the HeartBeat of the different systems """
 __tablename__ = 'heartbeat'
 __table_args__ = {'sqlite_autoincrement': True} # needed for sqlite. needed for pg ?

 id                = db.Column(db.Integer,primary_key=True)
 newest_heartbeat  = db.Column(db.String())     #:e.g. 2015-01-08 10:52:41
 system_id         = db.Column(db.String(10),unique=True)   #:e.g. SYSTEM_ID

 def __repr__(self):
     return '<system_id: %r <heartbeat: %r' % (self.system_id, self.newest_heartbeat)






