from ..utils import NamedEnum


class Statuses(NamedEnum):
    DRAFT = 'Draft'
    EDITING_REQUIRED = 'Editing required'
    READY_TO_PUBLISH = 'Ready to publish'
    PROOFREADING_REQUIRED = 'Proofreading required'
    PUBLISHED = 'Published'
