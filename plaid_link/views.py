from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from plaid_link.serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class UserCreate(APIView):
    """
    Creates the user.
    """
    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)