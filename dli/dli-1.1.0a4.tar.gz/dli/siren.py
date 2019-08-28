import requests
import re

from collections import namedtuple
from pypermedia.client import SirenBuilder
from pypermedia.siren import SirenEntity, _create_action_fn

import six

# regex to convert from camelCase to snake_case
_reg = re.compile(r'(?!^)(?<!_)([A-Z])')


def siren_to_dict(o):
    return {
        attr: getattr(o, attr)
        for attr in dir(o)
        if attr[:1] != '_' and not callable(getattr(o, attr))
    }


def siren_to_entity(o):
    """
    Helper method that converts a siren entity into a namedtuple
    """
    def value_to_entity(v):
        return siren_to_entity(v) if isinstance(v, dict) else v

    # pypermedia does not do recursive translation
    # so we might get a mix of objects or dicts in here
    attrs = siren_to_dict(o) if not isinstance(o, dict) else o
    attrs = {
        to_snake_case(key): value_to_entity(value)
        for key, value in six.iteritems(attrs)
    }
    return namedtuple(o.__class__.__name__, sorted(attrs))(**attrs)


def to_snake_case(s):
    # need to sanitise the string as in some cases the key might look like
    # 'Data Access' or 'Data Sensitivity'
    return _reg.sub(r'_\1', s.replace(' ', '_')).lower()


class PatchedSirenBuilder(SirenBuilder):
    def from_api_response(self, response):
        """Overriding to provide raw response data"""
        if not response.headers.get(
            'Content-Type', ''
        ).startswith('application/vnd.siren+json'):
            return None

        return super().from_api_response(response)

    def _construct_entity(self, entity_dict):
        """
        We need to patch the actions as there is no ``radio`` support
        on the current pypermedia version.

        To avoid code duplication, this function will attempt to call the parent
        and replace the created actions with our custom ones.
        """
        # pypermedia does not like any custom attributes
        # not even those in the spec
        for action in entity_dict.get("actions", []):
            if "allowed" in action:
                del action["allowed"]

        entity = super(PatchedSirenBuilder, self)._construct_entity(entity_dict)

        return PatchedSirenEntity(
            classnames=entity.classnames,
            properties=entity.properties,
            actions=entity.actions,
            links=entity.links,
            entities=entity.entities,
            rel=entity.rel,
            verify=entity.verify,
            request_factory=entity.request_factory
        )


def _patched_make_request(self, _session=None, verify=None, **kwfields):
    """ The purpose of this is to override the `SirenAction.make_request` in
        pypermedia, which ignores the passed `verify` argument and just uses
        the one defined on self, while the one passed into the function gets
        swallowed into `kwfields` and sent in the request.
    """
    if verify is None:
        verify = self.verify
    s = _session or requests.Session()
    return s.send(self.as_request(**kwfields), verify=verify)


class PatchedSirenEntity(SirenEntity):

    def as_python_object(self):
        ModelClass = type(str(self.get_primary_classname()), (), self.properties)

        siren_builder = PatchedSirenBuilder(verify=self.verify, request_factory=self.request_factory)
        # add actions as methods
        for action in self.actions:
            # patch make_request to resolve InsecureRequestWaring problems (see DL-1961)
            action.make_request = _patched_make_request.__get__(action, type(action))
            method_name = SirenEntity._create_python_method_name(action.name)
            method_def = _create_action_fn(action, siren_builder)
            setattr(ModelClass, method_name, method_def)

        # add links as methods
        for link in self.links:
            for rel in link.rel:
                method_name = SirenEntity._create_python_method_name(rel)
                siren_builder = PatchedSirenBuilder(verify=self.verify, request_factory=self.request_factory)
                method_def = _create_action_fn(link, siren_builder)

                setattr(ModelClass, method_name, method_def)

        def get_entity(obj, rel):
            matching_entities = self.get_entities(rel) or []
            for x in matching_entities:
                yield x.as_python_object()

        setattr(ModelClass, 'get_entities', get_entity)

        return ModelClass()
