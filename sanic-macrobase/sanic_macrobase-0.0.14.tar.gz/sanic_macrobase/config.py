from macrobase_driver.config import DriverConfig


class SanicDriverConfig(DriverConfig):

    LOGO: str = """
 _____       _
|  __ \     (_)               
| |  | |_ __ ___   _____ _ __ 
| |  | | '__| \ \ / / _ \ '__|
| |__| | |  | |\ V /  __/ |   
|_____/|_|  |_| \_/ \___|_|sanic
"""

    DEBUG: bool = False
    WORKERS: int = 1
    ACCESS_LOG: bool = True
    HEALTH_ENDPOINT: bool = True

    APP_HOST: str = '0.0.0.0'
    APP_PORT: int = 8000
    APP_BLUEPRINT: str = ''
