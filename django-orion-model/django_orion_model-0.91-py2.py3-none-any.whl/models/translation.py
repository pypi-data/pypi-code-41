from logging import getLogger

logger = getLogger(__name__)


class ModelTranslationOrionEntity:

    def fill_with_data(self, data):
        logger.debug("Filling object with %s", data)
        self.orion_id = data.get("id")
        self.orion_data = data
        self.orion_type = data.get("type")
        logger.debug("Orion fields  %s", self._orion_fields)
        for field in self._orion_fields:
                try:
                    if "_" in field.name:
                        # Some Fiware language specific codes
                        setattr(self, field.name, field.extract_from_json(data[field.name.replace("_eu","_eus").replace("_el","_gr").replace("_", ":")]))
                    else:
                        self.__dict__[field.name] = field.extract_from_json(data[field.name])
                except KeyError as ke:
                    logger.debug(ke)





