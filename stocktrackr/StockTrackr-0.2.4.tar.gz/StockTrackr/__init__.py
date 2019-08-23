# This package handles a lot of stuff that your operating system normally would (creating directories)
import os
try:
    from .av_api import get_intraday_data, get_daily_data, get_monthly_data, get_weekly_data
except:
    from av_api import get_intraday_data, get_daily_data, get_monthly_data, get_weekly_data
try:
    # This allows graphing
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    # This allows us to work with date objects
    from datetime import datetime
    # Allows us to wait
    from time import sleep
    # Pandas is used for dataframe manipulation
    import pandas as pd
    
except ImportError: # If packages don't exist, install them
    os.system('pip install alpha_vantage pandas datetime matplotlib')
    from alpha_vantage.timeseries import TimeSeries
    from datetime import datetime
    from time import sleep
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates


class Stox:
    def __init__(self):
        # Create all of the directories for .csv (Excel) files to be saved
        if not os.path.exists('./graphs'):
            os.makedirs('./graphs')
        if not os.path.exists('./data'):
            os.makedirs('./data')
        if not os.path.exists('./data/daily'):
            os.makedirs('./data/daily')
        if not os.path.exists('./data/monthly'):
            os.makedirs('./data/monthly')
        if not os.path.exists('./data/weekly'):
            os.makedirs('./data/weekly')
        if not os.path.exists('./data/intra'):
            os.makedirs('./data/intra')
        if not os.path.exists('./data/db'):
            os.makedirs('./data/db')
            
    def monitor_stock(self, ticker):
        print(f'Beginning monitor of stock {ticker}')
        while True:  # Always continue looping
            try:  # The try/except cause it to continue retrying if it fails to get the data the first time
                data = get_intraday_data(ticker, mode='return')
                data = data.loc[data['date'] == max(data['date'])]  # Select the row of data where the date column is equal to its maximum

                #Fancy print the data... the end and flush parameters are used to overwrite whatever was last printed
                print(f"Now: {datetime.now().time()} | Time: {data['date'].iloc[0]} | Open: {data['open'].iloc[0]} | High: {data['high'].iloc[0]} | Low: {data['low'].iloc[0]} | Close: {data['close'].iloc[0]} | Volume: {data['volume'].iloc[0]}", end='\r', flush=True)
                sleep(5)  # Wait 5 seconds after returning data

            except KeyError as e1:  # This catches the error that may arise when no data is returned
                print(e1)  # This literally means "do nothing"

            except KeyboardInterrupt:  # This catches when you use Command+C to escape the monitor
                print('Exiting monitoring...')
                return  # Exit the monitor function

    def command_loop(self, response):
        def pull_data():
            # Initialize variables that we will need
            r = ''
            tickers = []

            # This loop will collect a list of tickers to collect data of. The word 'done' causes it to end.
            while r != 'done':
                r = input('Enter a ticker or "done": ')
                if r != 'done':
                    # Append the user input to tickers if it's not done
                    tickers.append(r)

            # This is more advanced (I just learned you could do this) but its a list of functions so we can call them all
            fucntions = [get_intraday_data, get_daily_data, get_monthly_data, get_weekly_data]

            for t in tickers:  # Cycle through the tickers and get data for all of them
                for f in fucntions:  # Cycle through the different functions
                    s = False  # This boolean will become true only when a function was successful
                    while not s:  # While the data has not been saved, try to save it
                        try:
                            f(t)  # Try to perform the function
                            s = True  # This will only happen if the function was successful
                        except Exception as e:
                            print(e)
                            sleep(5)

        def monitor():
            # Get a stock to watch
            tick = input("Enter a ticker to monitor: ")
            self.monitor_stock(tick)
            

        d = {'pull': pull_data, 'monitor': monitor}
        d[response]()  # If response = 'pull' it will run pull_data, as shown above... Same for 'monitor'

    

    @staticmethod
    def UI():  # This isn't important but it basically just says "run this"
        stox = Stox()
        while True:  # Always continue running

            # Print 2 rows of lines to separate previous printed stuff
            print('-'*50)
            print('-'*50)

            # Fancy-ish (not really) UI stuff
            print('Enter one of the following:')
            print('\t"pull" to pull stock data to Excel')
            print('\t"monitor" to monitor a stock real-time')
            print('-'*50)

            # Get the users desired task and send it to the command loop which will call the right function
            r = input('X: ')
            stox.command_loop(r)

if __name__ == '__main__':
    Stox.UI()
