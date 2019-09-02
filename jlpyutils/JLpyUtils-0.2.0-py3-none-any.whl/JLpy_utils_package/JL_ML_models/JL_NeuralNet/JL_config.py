# config = tf.ConfigProto(log_device_placement=True) #restrict to cpu only: device_count={'GPU':0, 'CPU':4})
# config.gpu_options.allow_growth = True
# session = tf.Session(config=config)
# session.list_devices()