from rest_framework import generics
from users.serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class CreateUserView(generics.CreateAPIView):
    """create a new user"""

    serializer_class = CustomUserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """retrieve, update, delete created user"""

    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user
