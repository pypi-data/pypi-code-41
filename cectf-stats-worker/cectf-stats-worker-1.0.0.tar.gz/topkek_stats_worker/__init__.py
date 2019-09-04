from celery import Celery

app = Celery('cectf_stats_worker', broker='redis://localhost')


@app.task
def logit(x):
    print("Logging", x)
    return x
