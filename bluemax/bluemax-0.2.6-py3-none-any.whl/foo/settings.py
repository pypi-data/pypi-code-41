""" add your settings here """
import logging


def extend(settings):
    """ change settings """
    logging.info("extending settings")
    # settings["broadcaster"] = "bluemax.work.redis_broadcaster:RedisBroadcaster"
    settings.setdefault("tornado", {})["static_dir"] = "foo/static"
    # settings["tornado"]["manager"] = "bluemax.work:RedisManager"
    settings["redis_url"] = "redis://localhost:6379"
    settings["logging"] = "DEBUG"
    settings["debug"] = True
    return settings
