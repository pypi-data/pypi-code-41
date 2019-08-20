import wandb

def patch():
    mlflow = wandb.util.get_module("mlflow")
    from mlflow.tracking.client import MlflowClient
    client = MlflowClient()
    
    mlflow.orig_start_run = mlflow.start_run
    mlflow.orig_end_run = mlflow.end_run
    mlflow.orig_log_metric = mlflow.log_metric
    mlflow.orig_log_metrics = mlflow.log_metrics
    mlflow.orig_log_param = mlflow.log_param
    mlflow.orig_log_params = mlflow.log_params
    #mlflow.orig_delete_tag = mlflow.delete_tag
    mlflow.orig_set_tag = mlflow.set_tag
    mlflow.orig_set_tags = mlflow.set_tags
    mlflow.orig_set_experiment = mlflow.set_experiment
    mlflow.orig_log_artifact = mlflow.log_artifact
    mlflow.orig_log_artifacts = mlflow.log_artifacts

    def start_run(**kwargs):
        run = mlflow.orig_start_run(**kwargs)
        project = client.get_experiment(run.info.experiment_id).name
        wandb.init(id=run.info.run_id, project=project, name=False, config=run.data.tags, reinit=True)
        return run
    mlflow.start_run = start_run

    def end_run(status):
        # TODO: use status
        mlflow.orig_end_run(status)
        wandb.join()
    mlflow.end_run = end_run

    def log_param(key, value):
        mlflow.orig_log_param(key, value)
        wandb.config[key] = value
    mlflow.log_param = log_param

    def log_params(params):
        mlflow.orig_log_params(params)
        wandb.config.update(params)
    mlflow.log_params = log_params

    def log_metric(key, value, step=None):
        mlflow.orig_log_metric(key, value, step)
        wandb.log({key: value}, step=step)
    mlflow.log_metric = log_metric

    def log_metrics(metrics, step=None):
        mlflow.orig_log_metrics(metrics, step)
        wandb.log(metrics, step=step)
    mlflow.log_metrics = log_metrics
