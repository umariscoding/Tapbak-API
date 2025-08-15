from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['id'] = user.id
        return token


class CookieAuthentication():
    def set_refresh_token(self, response, refresh_token):
        response.set_cookie(
            'refresh_token',
            refresh_token,
            secure=True,  
            samesite='None',  # Set to 'Lax' for localhost development
            max_age=30*24*60*60,  # 30 days for refresh token
            path="/",
            httponly=True  # Prevent XSS attacks
        )
    
    def set_access_token(self, response, access_token):
        response.set_cookie(
            'access_token',
            access_token,
            secure=True,  # Set to False for localhost development
            samesite='None',  # Set to 'Lax' for localhost development
            max_age=15*60,  # 15 minutes for access token
            path="/",
            httponly=True  # Prevent XSS attacks
        )

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)
        request.data._mutable = True
        request.data['refresh'] = refresh_token
        request.data._mutable = False
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return Response({"error": "Failed to refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        else: 
            access_token = response.data['access']
            cookie_auth = CookieAuthentication()
            cookie_auth.set_access_token(response, access_token)
            cookie_auth.set_refresh_token(response, refresh_token)
        return response
    