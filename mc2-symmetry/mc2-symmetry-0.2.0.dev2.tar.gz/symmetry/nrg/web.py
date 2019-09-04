"""
   GET /services           returns all service descriptions
  POST /services           takes a json body of a service description

DELETE /services/<service> removes the metadata of the given service
   GET /services/<service> returns the service description of the given service

   GET /service/<service>/deployment    -> ServiceManager.info
  POST /service/<service>/deployment    -> ServiceManager.deploy
DELETE /service/<service>/deployment    -> ServiceManager.undeploy

TODO: potential extensions

PATCH /service/<service>/deployment -> Repair/converge to deployed state
"""
import logging

import falcon

from symmetry.api import ServiceMetadataRepository, ServiceDescription, ServiceManager

logger = logging.getLogger(__name__)


class ServicesResource:
    _repository: ServiceMetadataRepository

    def __init__(self, repository: ServiceMetadataRepository):
        self._repository = repository

    def on_get(self, req, resp):
        services = self._repository.get_services()
        logger.debug('got services %s', services)
        resp.media = [s.__dict__ for s in self._repository.get_services()]

    def on_post(self, req, resp):
        doc = req.media
        description = ServiceDescription(**doc)
        created = self._repository.save_service(description)
        resp.media = {
            'id': description.id,
            'created': created
        }


class ServiceResource:
    _repository: ServiceMetadataRepository

    def __init__(self, repository: ServiceMetadataRepository):
        self._repository = repository

    def on_get(self, req, resp, service_id):
        service = self._require_service(service_id)

        resp.media = service.__dict__

    def on_delete(self, req, resp, service_id):
        # TODO: only remove if there is no active deployment

        self._require_service(service_id)
        self._repository.remove_service(service_id)
        resp.media = 'OK'

    def _require_service(self, service_id):
        service = self._repository.get_service(service_id)
        if not service:
            raise falcon.HTTPNotFound()
        return service


class ServiceDeploymentResource:
    _service_manager: ServiceManager

    def __init__(self, service_manager: ServiceManager) -> None:
        super().__init__()
        self._service_manager = service_manager

    def on_get(self, req, resp, service_id):
        try:
            info = self._service_manager.info(service_id)
        except ValueError:
            raise falcon.HTTPNotFound()

        doc = dict()
        doc['description'] = info.description.__dict__
        doc['status'] = [status._asdict() for status in info.status]
        resp.media = doc

    def on_post(self, req, resp, service_id):
        description = self._service_manager.describe(service_id)
        if not description:
            raise falcon.HTTPNotFound()

        try:
            self._service_manager.deploy(service_id)
            resp.media = 'OK'
        except Exception as e:
            logger.exception('error while deploying service %s', service_id, e)
            raise falcon.HTTPBadRequest(title='error while deploying', description=str(e))

    def on_delete(self, req, resp, service_id):
        description = self._service_manager.describe(service_id)
        if not description:
            raise falcon.HTTPNotFound()

        try:
            self._service_manager.undeploy(service_id)
            resp.media = 'OK'
        except Exception as e:
            logger.exception('error while undeploying service %s', service_id, e)
            raise falcon.HTTPBadRequest(title='error while undeploying', description=str(e))
