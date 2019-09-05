from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.exception.model_exception.inspetor_event_exception import InspetorEventException


class InspetorEvent(InspetorAbstractModel):

    DRAFT_STATUS     = "draft"
    PRIVATE_STATUS   = "private"
    PUBLISHED_STATUS = "published"
    OTHER_STATUS     = "other"

    def __init__(self, categories = None, address = None,
        admins_id = None, seating_options = None, timestamp = None):
        self.id = None
        self.name = None
        self.description = None
        self.sessions = None
        self.status = None
        self.status_other = None
        self.slug = None
        self.creator_id = None
        self.is_physical = True
        self._categories = categories
        self._address = address
        self._admins_id = admins_id
        self._seating_options = seating_options
        self._timestamp = timestamp

    def is_valid(self):
        if self.id is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_ID
            )

        if self.name is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_NAME
            )

        if self._timestamp is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_TIMESTAMP
            )

        if self.creator_id is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_CREATOR_ID
            )

        if self._admins_id is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_ADMINS_ID
            )

        if self.is_physical is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_IS_PHYSICAL
            )

        if self.is_physical is True:
            if self._address is None:
                raise InspetorEventException(
                    InspetorEventException.REQUIRED_EVENT_ADDRESS
                )

        if self.sessions is None or self.sessions == []:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_SESSIONS
            )

        if self.status is not None:
            self.validate_status()

    def is_valid_update(self):
        if self.id is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_ID
            )

        if self._timestamp is None:
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_TIMESTAMP
            )

        if self.status is not None:
            self.validate_status()

    def validate_status(self):
        all_status = [
            "draft",
            "private",
            "published"
        ]

        if not self.status in all_status:
            self.status_other = self.status
            self.status = "other"

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        if address is not None:
            address.is_valid()

        self._address = address

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = self.inspetor_date_formatter(timestamp)

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def admins_id(self):
        return self._admins_id

    @admins_id.setter
    def admins_id(self, admins_id):
        if not isinstance(admins_id, list):
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_ADMINS_ID
            )
        for admin in admins_id:
            if admin is None:
                raise InspetorEventException(
                    InspetorEventException.REQUIRED_EVENT_ADMINS_ID
                )

        self._admins_id = admins_id

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def seating_options(self):
        return self._seating_options

    @seating_options.setter
    def seating_options(self, seating_options):
        if not isinstance(seating_options, list):
            raise InspetorEventException(
                InspetorEventException.REQUIRED_EVENT_SEATING_OPTIONS
            )
        for option in seating_options:
            if option is None:
                raise InspetorEventException(
                    InspetorEventException.REQUIRED_EVENT_SEATING_OPTIONS
                )

        self._seating_options = seating_options

    #To understand this part, please read https://bit.ly/2ywz8PN
    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, categories):
        if categories is not None:
            for category in categories:
                if category is not None:
                    category.is_valid()

        self._categories = categories

    def jsonSerialize(self):
        return {
            "event_id"              : self.encode_data(self.id),
            "event_name"            : self.encode_data(self.name),
            "event_description"     : self.encode_data(self.description),
            "event_timestamp"  		: self.encode_data(self.timestamp),
            "event_sessions"        : self.encode_array(self.sessions, True),
            "event_status"          : self.encode_data(self.status),
			"event_status_other"    : self.encode_data(self.status_other),
			"event_seating_options" : self.encode_array(self.seating_options, False),
            "event_categories"      : self.encode_array(self.categories, True),
            "event_address"         : self.encodeObject(self.address),
            "event_slug"            : self.encode_data(self.slug),
            "event_creator_id"      : self.encode_data(self.creator_id),
			"event_admins_id"       : self.encode_array(self.admins_id, False),
			"event_is_physical"		: self.encode_data(self.is_physical)
        }
