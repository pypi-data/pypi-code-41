# from flask import Blueprint, request
# from bin.common.AppConstants import AuditConfiguration
# from bin.common.AppConstants import RequestMethods
# # from bin.core.applications.AuditManagement import AuditManagementControl
# from bin.util import Logging as Log
# import traceback
#
# Logger = Log.get_logger()
#
# audit_configuration_blueprint = Blueprint(AuditConfiguration.service_blueprint, __name__)
#
#
#
# @audit_configuration_blueprint.route(AuditConfiguration.api_get_model, methods=[RequestMethods.POST])
# def get_api_model():
#     """
#     This service is to call the save audit function.
#     """
#     try:
#         if request.method == 'POST':
#             handler_object = AuditManagementControl()
#             result =handler_object.save_audit_entry()
#     except Exception as e:
#         Logger.exception('Exception occured due to ', str(e))
#         traceback.print_exc()