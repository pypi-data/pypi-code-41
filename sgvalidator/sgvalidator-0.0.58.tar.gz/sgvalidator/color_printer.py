import termcolor


class ColorPrinter:
    @staticmethod
    def printGreen(message):
        ColorPrinter._printColor(message, "green")

    @staticmethod
    def printGreenBanner(message):
        ColorPrinter._printColor(message, "green", attrs=['reverse'])

    @staticmethod
    def getRedBanner(message):
        ColorPrinter._getColoredText(message, "red", attrs=['reverse'])

    @staticmethod
    def printYellow(message):
        ColorPrinter._printColor(message, "yellow")

    @staticmethod
    def printYellowBanner(message):
        ColorPrinter._printColor(message, "yellow", attrs=['reverse'])

    @staticmethod
    def printCyanBanner(message):
        ColorPrinter._printColor(message, "cyan", attrs=['reverse'])

    @staticmethod
    def printRed(message):
        ColorPrinter._printColor(message, "red")

    @staticmethod
    def printBlueBanner(message):
        ColorPrinter._printColor(message, "blue", attrs=['reverse'])

    @staticmethod
    def printWhiteBanner(message):
        ColorPrinter._printColor(message, "white", attrs=['reverse'])

    @staticmethod
    def printRedBanner(message):
        ColorPrinter._printColor(message, "red", attrs=['reverse'])

    @staticmethod
    def printCyan(message):
        ColorPrinter._printColor(message, "cyan")

    @staticmethod
    def _printColor(message, color, attrs=None):
        print(termcolor.colored(message, color, attrs=attrs))

    @staticmethod
    def _getColoredText(message, color, attrs=None):
        return termcolor.colored(message, color, attrs=attrs)
