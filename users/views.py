from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404

from .serializers import RegisterSerializer, UserProfileSerializer, UserDetailSerializer
from .models import User
from .tokens import email_verification_token
from .utils import send_verification_email
from core.throttling import AuthRateThrottle, SensitiveEndpointThrottle
from community.models import Group, Post
from community.serializers import GroupListSerializer, PostListSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send verification email
        send_verification_email(request, user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'User registered successfully. Please check your email to verify your account.',
                'user': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return Response(
            {'message': 'Email successfully verified. You can now log in.'},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'Verification link is invalid or has expired.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None):
        user = self.get_object()
        groups = Group.objects.filter(created_by=user)
        serializer = GroupListSerializer(groups, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        user = self.get_object()
        posts = Post.objects.filter(author=user)
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
