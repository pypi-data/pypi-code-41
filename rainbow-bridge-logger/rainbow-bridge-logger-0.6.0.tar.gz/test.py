from rainbow import RainbowLogger

if __name__ == '__main__':
  logger = RainbowLogger(__name__)
  logger.info('my info')
  logger.warning('my warn')
  logger.error('my error')
  logger.debug('my debug')
