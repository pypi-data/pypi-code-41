from .base import Base

class CardBin(Base):

    def __init__(self, merchant, environment):

        super(CardBin, self).__init__(merchant)

        self.environment = environment

    def execute(self, bin):

        uri = '%s1/cardBin/%s' % (self.environment.api_query, bin)

        return self.send_request('GET', uri)