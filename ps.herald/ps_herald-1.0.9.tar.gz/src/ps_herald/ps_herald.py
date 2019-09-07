import sys,os
l = os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1]
#print(l[0])
sys.path.append(l[0])

from ps_herald import create_app, db, cli
from ps_herald.models import User, Post,Log

app = create_app()
cli.register(app)
app.run()
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
