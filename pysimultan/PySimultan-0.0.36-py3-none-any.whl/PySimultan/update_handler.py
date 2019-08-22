
class UpdateHandler(object):

    def __init__(self):

        self._Cache = []
        self._BulkUpdate = False

    def add_notification(self, cb, at):

        if self._Cache.__len__() > 0:
            if not(any(x.CB[0] == cb for x in self._Cache)):
                self._Cache.append(Notifcation(cb, at))
            else:
                notification = next((x for x in self._Cache if x.CB[0] == cb), None)
                notification.add_attribute(at)
        else:
            self._Cache.append(Notifcation(cb, at))

        if not self._BulkUpdate:
            self.notify_observers()

    def notify_observers(self):
        for notification in self._Cache:
            for at in notification.AT:
                notification.CB[0](ChangedAttribute=at)
        self._Cache = []

    @property
    def BulkUpdate(self):
        return self._BulkUpdate

    @BulkUpdate.setter
    def BulkUpdate(self, value):
        initial_value = self._BulkUpdate
        self._BulkUpdate = value

        if not self._BulkUpdate and initial_value:
            self.notify_observers()


class Notifcation(object):

    def __init__(self, cb, att=None):

        self.CB = [cb]

        if att is None:
            self.AT = []
        else:
            self.AT = [att]

    def add_attribute(self, at):
        if not(at in self.AT):
            self.AT.append(at)
