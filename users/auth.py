from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth import authenticate


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Authenticate user
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        user = authenticate(**authenticate_kwargs)
        
        # Check if user exists and is active
        if user is None:
            raise serializers.ValidationError(
                'No active account found with the given credentials',
                code='authorization'
            )
            
        # Check if email is verified
        if not user.is_email_verified:
            raise serializers.ValidationError(
                'Email not verified. Please check your email for verification link.',
                code='email_not_verified'
            )
            
        # Get the token
        data = super().validate(attrs)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except serializers.ValidationError as e:
            if 'email_not_verified' in e.get_codes():
                return Response(
                    {'error': e.detail[0]},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {'error': e.detail},
                status=status.HTTP_401_UNAUTHORIZED
            )
