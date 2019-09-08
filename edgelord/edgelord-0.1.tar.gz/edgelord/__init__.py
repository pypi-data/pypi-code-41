from . import (
    security,
    security_data
)

# Classes
data = security_data.security_data
security = security.security

def from_csv(file):
    

    return security().from_csv(file)

def previous_business_day(days = 1):
    """Return the date for the last business day"""

    today = pandas.datetime.today()
    today = str(today - BDay(days)).split(" ")[0]
    today = today.split("-")
    today = datetime(int(today[0]), int(today[1]), int(today[2]))

    return today