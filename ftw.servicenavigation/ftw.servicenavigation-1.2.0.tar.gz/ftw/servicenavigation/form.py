from Acquisition import aq_base
from collective.z3cform.datagridfield import DataGridFieldFactory
from datetime import datetime
from ftw.servicenavigation import _
from path import Path
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder
from plone.supermodel import model
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.form import EditForm
from z3c.relationfield import RelationChoice
from z3c.relationfield import RelationValue
from zope import schema
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import yaml


ANNOTATION_KEY = 'ftw.servicenavigation.service_navigation'
ICONS_PATH = Path(__file__).dirname() + '/resources/icons.yml'
ICONS = []


with ICONS_PATH.open('rb') as icons_file:
    ICONS = yaml.load(icons_file)['icons']


def create_relation_for(obj):
    intids = getUtility(IIntIds)
    intid = intids.getId(aq_base(obj))
    return RelationValue(intid)


def icons(context):
    terms = [SimpleVocabulary.createTerm('no-icon', 'no-icon', '-')]

    for icon in ICONS:
        terms.append(
            SimpleVocabulary.createTerm(icon['id'], icon['id'], icon['name']))
    return SimpleVocabulary(terms)

alsoProvides(icons, IContextSourceBinder)


class IServiceNavigationSchemaGrid(model.Schema):

    label = schema.TextLine(
        title=_(u'Label'),
        required=True,
    )

    icon = schema.Choice(
        title=_(u'label_icon', default=u'Icon'),
        required=True,
        source=icons,
    )

    external_url = schema.TextLine(
        title=_(u'label_external_url', default=u'External URL'),
        required=False,
    )

    directives.widget('internal_link', ContentTreeFieldWidget)
    internal_link = RelationChoice(
        title=_(u'label_internal_link', default=u'Internal link'),
        source=PathSourceBinder(),
        required=False,
    )

    blank = schema.Bool(
        title=_(u'label_blank', default=u'Open in new window'),
        required=False,
        default=False,
        missing_value=False,
    )


class IServiceNavigationSchema(model.Schema):
    directives.widget('links', DataGridFieldFactory, allow_reorder=True)
    links = schema.List(
        title=_(u'label_service_links', default=u'Service links'),
        value_type=schema.Object(
            title=u'link',
            schema=IServiceNavigationSchemaGrid
        ),
        required=False,
        missing_value=[],
    )

    disable = schema.Bool(
        title=_(u'label_disable_service_links',
                default=u'Disable service links'),
        required=False,
        missing_value=False,
    )

    directives.mode(modified='hidden')
    modified = schema.Bool(
        title=u'modified_marker',
        required=False,
        default=True,
        missing_value=True,
    )

    @invariant
    def link_validator(data):
        for link in data.links:
            if link.get('internal_link', None) and link.get('external_url', None):
                raise Invalid(_('error_link_validator',
                                u'Choose between an external or an internal link.'))


class ServiceNavigationConfig(object):
    implements(IServiceNavigationSchema)

    def __init__(self, storage):
        self.storage = storage

    def __getattr__(self, name):
        if name == 'storage':
            return object.__getattr__(self, name)
        value = self.storage.get(name)
        return value

    def __setattr__(self, name, value):
        if name == 'storage':
            return object.__setattr__(self, name, value)
        if name == 'links':
            self.storage[name] = PersistentList(map(PersistentMapping, value))
            return

        if name == 'disable':
            self.storage[name] = value
            return

        if name == 'modified':
            self.storage[name] = str(datetime.now())
            return

        raise AttributeError(name)


class ServiceLinksRow(object):
    implements(IServiceNavigationSchemaGrid)

    def __init__(self, storage):
        self.storage = storage

    def __getattr__(self, name):
        if name == 'storage':
            return object.__getattr__(self, name)
        value = self.storage.get(name)

        # Without plone.app.relationfield this *hack* would not be necessary.
        # Check https://github.com/plone/plone.app.relationfield/blob/1.2.1/plone/app/relationfield/widget.zcml
        # It changes how the widget behaves with stored values.
        # With plone.app.relationfield a RelationValue is needed, whithout the
        # Path if you're using the PathSourceBinder.

        # Start hack
        if value and name == 'internal_link':
            try:
                obj = getSite().unrestrictedTraverse(value.lstrip('/'))
                value = create_relation_for(obj)
            except KeyError:
                value = None
        # End hack

        return value


class ServiceNavigationForm(AutoExtensibleForm, EditForm):
    template = ViewPageTemplateFile('templates/form.pt')

    schema = IServiceNavigationSchema
    ignoreContext = False
    name = "service-edit-form"

    label = _(u'label_service_navigation', default=u'Service navigation')

    @button.buttonAndHandler(pmf(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            pmf(u"Changes saved"),
        )
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(pmf(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            pmf(u"Edit cancelled"),
        )
        self.request.response.redirect(self.context.absolute_url())

    def updateActions(self):
        super(EditForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")

    def getContent(self):
        annotations = IAnnotations(self.context)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = PersistentMapping()
        return ServiceNavigationConfig(annotations[ANNOTATION_KEY])
