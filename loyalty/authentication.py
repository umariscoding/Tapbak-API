from rest_framework_simplejwt.authentication import JWTAuthentication
from loyalty.models import Vendor

class CookieJWTAuthentication(JWTAuthentication):

    def get_raw_token(self, header):
        request =  self.request
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        access_token = auth_header.split(' ')[1]
        if not access_token:
            return None
        return access_token
    
    def authenticate(self, request):
        self.request = request
        raw_token = self.get_raw_token(None) 
        
        # If no token is present, return None (no authentication)
        if not raw_token:
            return None
            
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            user_auth_tuple = (user, validated_token)
            return user_auth_tuple
        except Exception as e:
            return None
    
    def get_user(self, validated_token):
        user_id = validated_token['user_id']
        user = Vendor.objects.get(id=user_id)
        return user
        