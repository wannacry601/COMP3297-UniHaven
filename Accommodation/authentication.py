from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UniversityToken

class UniversityTokenAuthentication(TokenAuthentication):
    
    def authenticate(self, request):
        auth_result = super().authenticate(request)
        if not auth_result:
            return None
            
        user, token = auth_result
        
        try:
            university_token = UniversityToken.objects.select_related('university').get(token=token)
            request.university_id = university_token.university_id
            request.university_name = university_token.university.name
            return (user, token)
        except UniversityToken.DoesNotExist:
            raise AuthenticationFailed('Token not associated with any university')