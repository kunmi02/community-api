from rest_framework import serializers
from .models import Group, Post, Comment, GroupMembership
from users.models import User

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_picture')


class CommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at', 'updated_at', 'parent', 'replies_count')
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class PostListSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'slug', 'content', 'group', 'group_name', 'author', 
                  'created_at', 'updated_at', 'image', 'comments_count', 'likes_count', 'is_liked')
        read_only_fields = ['author', 'created_at', 'updated_at', 'slug']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class PostDetailSerializer(PostListSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ('comments',)
    
    def get_comments(self, obj):
        # Only get top-level comments (no parent)
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True).data


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ('id', 'user', 'group', 'role', 'joined_at')
        read_only_fields = ['joined_at']


class GroupListSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'slug', 'description', 'cover_image', 'created_by', 
                  'created_at', 'updated_at', 'is_public', 'members_count', 'posts_count')
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'slug']
    
    def get_members_count(self, obj):
        return obj.members.count()
    
    def get_posts_count(self, obj):
        return obj.posts.count()


class GroupDetailSerializer(GroupListSerializer):
    recent_posts = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta(GroupListSerializer.Meta):
        fields = GroupListSerializer.Meta.fields + ('recent_posts', 'is_member', 'user_role')
    
    def get_recent_posts(self, obj):
        posts = obj.posts.all()[:5]  # Get 5 most recent posts
        return PostListSerializer(posts, many=True, context=self.context).data
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and self.get_is_member(obj):
            membership = GroupMembership.objects.get(user=request.user, group=obj)
            return membership.role
        return None
