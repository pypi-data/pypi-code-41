def deploy_model(url,release='canary'):
    status = {
        'status': 'Successfully deployed to '+ release,
        'Model serving path': 'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/'+release+'/7398hg/invocation'
    }
    return status