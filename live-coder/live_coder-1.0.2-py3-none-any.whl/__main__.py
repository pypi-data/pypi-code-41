from sys import argv as arguments
PORT = int(arguments[1])

from live_coder.server import app

app.run(host='0.0.0.0', port=PORT, debug=False)
