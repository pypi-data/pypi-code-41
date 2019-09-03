import dash
from nqontrol import settings
from nqontrol.nqontrolUI import UI


def getLayout(ui):
    return ui.layout


app = dash.Dash(__name__)

ui = UI(app)
app.layout = getLayout(ui)
ui.setCallbacks()
server = app.server


def main():
    app.run_server(host='0.0.0.0', debug=settings.DEBUG, threaded=False, processes=1)


if __name__ == '__main__':
    main()
