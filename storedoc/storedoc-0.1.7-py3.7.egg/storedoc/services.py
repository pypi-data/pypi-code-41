from storedoc.local import LocalStorage
from storedoc.s3 import S3Service
from storedoc.spaces import DOService


SUPPORTED_SERVICES = {
    'local': {
        'service': LocalStorage,
        'description': 'Store locally'
    },
    's3': {
        'service': S3Service,
        'description': 'Amazon S3 or Amazon Simple Storage Service is\
a "simple storage service" offered by Amazon Web Services that provides object storage through a web service interface.'
    },
    'aws': {
        'service': S3Service,
        'description': 'Amazon S3 or Amazon Simple Storage Service is\
a "simple storage service" offered by Amazon Web Services that provides object storage through a web service interface.'
    },
    'spaces': {
        'service': DOService,
        'description': 'DigitalOcean Spaces are ideal for storing static, unstructured\
data like audio, video, and images as well as large amounts of text'
    },
    'do': {
        'service': DOService,
        'description': 'DigitalOcean Spaces are ideal for storing static, unstructured\
data like audio, video, and images as well as large amounts of text'
    }
}