from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly 
from rest_framework import generics
from rest_framework.views import APIView
from . import serializers
from .models import EmailUser
from .permissions import IsSelfOrReadOnly

class RegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny,]
    serializer_class = serializers.EmailUserSerializer


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsSelfOrReadOnly]
    serializer_class = serializers.EmailUserSerializer
    queryset = EmailUser.objects.all()
