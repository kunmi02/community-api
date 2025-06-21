from rest_framework import generics, permissions, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Group, Post, Comment, GroupMembership
from .serializers import (
    GroupListSerializer, GroupDetailSerializer, 
    PostListSerializer, PostDetailSerializer,
    CommentSerializer, GroupMembershipSerializer
)


class IsGroupMemberOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow group members to create posts."""
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to group members
        group_id = request.data.get('group')
        if not group_id:
            return False
            
        try:
            group = Group.objects.get(id=group_id)
            return group.members.filter(id=request.user.id).exists() or group.created_by == request.user
        except Group.DoesNotExist:
            return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow authors of an object to edit it."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the author
        return obj.author == request.user


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GroupDetailSerializer
        return GroupListSerializer
    
    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        # Add creator as admin member
        GroupMembership.objects.create(user=self.request.user, group=group, role='admin')
    
    def get_queryset(self):
        queryset = Group.objects.all()
        
        # Filter by public status for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, slug=None):
        group = self.get_object()
        
        # Check if user is already a member
        if group.members.filter(id=request.user.id).exists():
            return Response({'detail': 'You are already a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Add user as member
        GroupMembership.objects.create(user=request.user, group=group, role='member')
        return Response({'detail': 'Successfully joined the group.'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, slug=None):
        group = self.get_object()
        
        # Check if user is a member
        if not group.members.filter(id=request.user.id).exists():
            return Response({'detail': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is the creator
        if group.created_by == request.user:
            return Response({'detail': 'Group creator cannot leave the group.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove user from group
        GroupMembership.objects.filter(user=request.user, group=group).delete()
        return Response({'detail': 'Successfully left the group.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def members(self, request, slug=None):
        group = self.get_object()
        memberships = GroupMembership.objects.filter(group=group)
        serializer = GroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        group = self.get_object()
        posts = Post.objects.filter(group=group)
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def get_queryset(self):
        queryset = Post.objects.all()
        
        # Filter by group if specified
        group_slug = self.request.query_params.get('group', None)
        if group_slug is not None:
            queryset = queryset.filter(group__slug=group_slug)
        
        # Filter by public groups for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(group__is_public=True)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        post = self.get_object()
        
        # Check if user already liked the post
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            return Response({'detail': 'Post unliked.'}, status=status.HTTP_200_OK)
        else:
            post.likes.add(request.user)
            return Response({'detail': 'Post liked.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, slug=None):
        post = self.get_object()
        
        # Get comment data
        content = request.data.get('content')
        parent_id = request.data.get('parent', None)
        
        if not content:
            return Response({'detail': 'Comment content is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create comment
        comment_data = {
            'post': post,
            'author': request.user,
            'content': content
        }
        
        # Add parent if it's a reply
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
                comment_data['parent'] = parent
            except Comment.DoesNotExist:
                return Response({'detail': 'Parent comment not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(**comment_data)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PublicFeedView(generics.ListAPIView):
    """View for the public feed of posts across all groups."""
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        # For authenticated users, show posts from public groups and groups they're members of
        if self.request.user.is_authenticated:
            user_groups = self.request.user.joined_groups.all()
            return Post.objects.filter(
                Q(group__is_public=True) | Q(group__in=user_groups)
            ).order_by('-created_at')
        
        # For non-authenticated users, only show posts from public groups
        return Post.objects.filter(group__is_public=True).order_by('-created_at')
