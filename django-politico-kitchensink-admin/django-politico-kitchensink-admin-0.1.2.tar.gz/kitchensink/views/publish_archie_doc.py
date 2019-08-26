import requests
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kitchensink.conf import settings
from kitchensink.models import ArchieDoc
from kitchensink.utils.api_auth import TokenAPIAuthentication


class PublishArchieDoc(APIView):
    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return ArchieDoc.objects.get(pk=pk)
        except ArchieDoc.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        doc = self.get_object(pk)
        r = requests.post(
            settings.API_ENDPOINT,
            json={
                "archieDoc": doc.doc_id,
                "publish": True,
                "schema": doc.validation_schema,
            },
        )
        if r.status_code != requests.codes.ok:
            return Response(r.content, status=r.status_code)
        return Response(r.json(), status=status.HTTP_200_OK)
