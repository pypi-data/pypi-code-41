import logging
import os
import signal

from symmetry.webapp.ws.websocket import WebsocketServer

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    def handler(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    redis_address = (os.getenv('symmetry_redis_host', 'localhost'), int(os.getenv('symmetry_redis_port', 6379)))

    ws_server = WebsocketServer(redis_address=redis_address)
    try:
        logger.info("running websocket server...")
        ws_server.run()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("stopping websocket server...")
        ws_server.stop()
        logger.info("websocket server exiting")


if __name__ == '__main__':
    main()
