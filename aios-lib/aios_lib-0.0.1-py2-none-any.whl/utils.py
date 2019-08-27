'''
'''
import os
import requests
import json
import tensorflow as tf
import threading

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin


def get_env(env_name):
    try:
        env = os.environ[env_name]
    except:
        raise ValueError(
            "There is no environment variable called %s!" % (env_name))
    return env


def get_data_dir():
    data_dir = get_env("CLUSTAR_DATA_DIR")
    if not os.path.exists(data_dir):
        raise ValueError("The CLUSTAR_DATA_DIR does not exist")
    return data_dir


def get_model_dir():
    model_dir = get_env("CLUSTAR_MODEL_DIR")
    if not os.path.exists(model_dir):
        raise ValueError("The CLUSTAR_MODEL_DIR does not exist")
    return model_dir


def get_worker_gpu_num():
    num_gpu = get_env("CLUSTAR_WORKER_GPU_NUM")
    if (int(num_gpu) == 0):
        tf.logging.warning(
            "Every worker has 0 gpu, tensorflow will run CPU TRAINING")
        # TODO: check current distributed strategy support cpu training or not.
        return 0

    return num_gpu


def get_evaluator_gpu_num():
    num_gpu = get_env("CLUSTAR_EVALUATOR_GPU_NUM")
    if (num_gpu == 0):
        # TODO: how to run evaluator in cpu only environment?
        tf.logging.warning(
            "Every evaluator has 0 gpu, this may lead to a evaluation error")
        return 0

    return num_gpu

# TODO:how to handle 0 gpu per worker?


def get_train_distribution():
    distribution = get_env("CLUSTAR_TRAIN_DISTRIBUTION")
    num_gpu = get_worker_gpu_num()
    if (distribution == "ParameterServer"):
        distribution_obj = tf.contrib.distribute.ParameterServerStrategy(
            int(num_gpu))
    elif (distribution == "RingAllReduce"):
        distribution_obj = tf.contrib.distribute.CollectiveAllReduceStrategy(
            int(num_gpu))
    else:
        raise ValueError(
            "available distribution string is 'ParameterServer' "
            "and 'RingAllReduce', but now is " % distribution)

    return None

# TODO:how to handle 0 gpu per worker?


def get_eval_distribution():
    distribution = get_env("CLUSTAR_TRAIN_DISTRIBUTION")
    num_gpu = get_evaluator_gpu_num()
    if int(num_gpu) > 1: 
        if (distribution == "ParameterServer"):
            distribution_obj = tf.contrib.distribute.ParameterServerStrategy(
                int(num_gpu))
        elif (distribution == "RingAllReduce"):
            distribution_obj = tf.contrib.distribute.CollectiveAllReduceStrategy(
                int(num_gpu))
        else:
            raise ValueError(
                "available distribution string is 'ParameterServer' "
                "and 'RingAllReduce', but now is " % distribution)
        return distribution_obj

    elif int(num_gpu) == 1:
        return None
    else:
        raise ValueError("Evaluator should have at least one GPU")

def post_top1_metric(score, global_step):
    task_name = get_env("CLUSTAR_TASK_NAME")
    url = urljoin(get_env("CLUSTAR_AIOS_HOST"), "/report-score")
    data = json.dumps(
        {"task_name": task_name, "score": str(score), "global_step": str(global_step)})
    requests.post(url, data=data)


def report_top1_metric(score, global_step):
    t = threading.Thread(target=post_top1_metric, args=(score, global_step))
    t.start()


def post_train_loss(loss, global_step):
    task_name = get_env("CLUSTAR_TASK_NAME")
    url = urljoin(get_env("CLUSTAR_AIOS_HOST"), "/report-loss")
    data = json.dumps(
        {"task_name": task_name, "loss": str(loss), "global_step": str(global_step)})
    requests.post(url, data=data)

def report_top1_loss(loss, global_step):
    t = threading.Thread(target=post_train_loss, args=(loss, golbal_step))
    t.start()


class EstimatorBuilder:

    def __init__(self):
        # model_fn help tensorflow to build compute graph.
        self._model_fn = None

        # model_dir decided where to save models during training.
        self._model_dir = None

        # tf_random_seed random seed for tensorflow initializers.
        self._tf_random_seed = None

        # specifies after how many step estimator save summary to disk.
        self._save_summary_steps = 100

        # hyper params passed to estimator.
        self._hyper_params = None

        # save_checkpoints_steps specifies after how
        # many step estimator save model to disk.
        self._save_checkpoints_steps = 50

        # save_checkpoints_secs specifies after how
        # many second estimator save model to disk.
        self._save_checkpoints_secs = None

        # session config of tensorflow session.
        self._session_config = None

        # maximum number of recent checkpoint files to keep
        self._keep_checkpoint_max = 5

        # The frequency, in number of global steps, that the
        # global step and the loss will be logged during training.
        self._log_step_count_steps = 100

        # enable loss reporter
        self._enable_loss_reporter = False

        # enable eval reporter
        self._enable_eval_reporter = True

    def set_hyper_parameter(self, hyper_params):
        self._hyper_params = hyper_params

    def set_model_fn(self, model_fn):
        self._model_fn = model_fn

    def set_tf_random_seed(self, seed):
        self._tf_random_seed = seed

    def set_save_summary_steps(self, save_summary_steps):
        self._save_summary_steps = save_summary_steps

    def set_save_checkpoints_secs(self, save_checkpoints_secs):
        self._save_checkpoints_secs = save_checkpoints_secs

    def set_save_checkpoints_steps(self, save_checkpoints_steps):
        self._save_checkpoints_steps

    def set_session_config(self, session_config):
        self._session_config = session_config

    def set_keep_checkpoint_max(self, keep_checkpoint_max):
        self._keep_checkpoint_max = keep_checkpoint_max

    def set_log_step_count_steps(self, log_step_count_steps):
        self._log_step_count_steps = log_step_count_steps

    def enable_loss_upload(self):
        self._enable_loss_reporter = True

    def enable_eval_upload(self):
        self._enable_eval_reporter = True

    def build_estimator(self):

        if self._model_fn is not None:
            tf.logging.info(
                "aleady set model_fn, estimator will use "
                "this function to construct compute graph.")
        else:
            raise ValueError(
                "No 'model_fn' found, please provide 'model_fn'"
                " by run 'EstimatorBuilder.set_model_fn'")

        if self._tf_random_seed is not None:
            tf.logging.info(
                "tf_random_seed in run_config is %d." % self._tf_random_seed)

        if self._hyper_params is not None:
            tf.logging.info(
                "aleady set hyper parameter:{}".format(self._hyper_params))
        else:
            raise ValueError(
                "No hyper parameter found, please provide hyper "
                "paramter by run 'EstimatorBuilder.set_hyper_params'")

        self._model_dir = get_model_dir()
        tf.logging.info(
            "estimator will save checkpoint and summery files to %s" % self._model_dir)

        tf.logging.info("after every %d steps during training, "
                        "estimator will save new checkpoints." %
                        self._save_checkpoints_steps)

        train_distribution = get_train_distribution()
        eval_distribution = get_eval_distribution()

        tf.logging.info("after every %d steps, tensorflow will output"
                        " global step and loss during train." %
                        self._log_step_count_steps)

        if self._enable_loss_reporter == True:
            tf.logging.info("estimator will report loss value every 10 steps.")
        else:
            tf.logging.info("estimator will not report any loss value.")

        if self._enable_eval_reporter == True:
            tf.logging.info(
                "estimator will report evaluation matric after every evaluation finish.")
        else:
            tf.logging.info("estimator will not report any loss value.")

        run_config = tf.estimator.RunConfig(
            model_dir = self._model_dir,
            tf_random_seed = self._tf_random_seed,
            session_config = self._session_config,
            # distribute 
            eval_distribute = eval_distribution,
            train_distribute = None,
            log_step_count_steps = self._log_step_count_steps,

            # TODO:one of below two options must be None, check it.
            save_checkpoints_secs = self._save_checkpoints_secs,
            save_checkpoints_steps = self._save_checkpoints_steps)

        estimator = tf.estimator.Estimator(
            model_fn=self._model_fn,
            model_dir=self._model_dir,
            config=run_config,
            params=self._hyper_params)

        # upload top-1 accuracy metric if necessary.
        # TODO:support more custom metric, not only top-1 accuracy.
        if self._enable_eval_reporter:
            estimator.enable_eval_reporter(report_top1_metric)

        # upload training loss if necessary.
        if self._enable_loss_reporter:
            estimator.enable_loss_reporter(report_train_loss)

        return estimator

if __name__ == "__main__":
    get_data_dir()
    get_model_dir()
    report_score(1)
