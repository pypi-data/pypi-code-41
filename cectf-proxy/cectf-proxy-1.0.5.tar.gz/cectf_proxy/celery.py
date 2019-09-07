from celery import Celery
from mongoengine import connect

app = Celery('cectf_proxy', broker='redis://localhost')

if __name__ == '__main__':
    connect('test')
    app.start()
