import os

class Configuration:
    # The default API url base is set by the API library
    STIB_BASE = os.environ.get('STIB_BASE', None)

    STIB_CLIENT_ID = os.environ.get('STIB_CLIENT_ID')
    STIB_CLIENT_SECRET = os.environ.get('STIB_CLIENT_SECRET')

    DEFAULT_ROUTES = ['1', '5', '2', '6', '3', '7']
