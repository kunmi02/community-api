from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from community.models import Group, Post

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'bio', 'profile_picture', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')


class UserDetailSerializer(serializers.ModelSerializer):
    created_groups_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'bio', 'profile_picture', 
                  'date_joined', 'created_groups_count', 'posts_count')
        read_only_fields = ('id', 'email', 'date_joined')

    def get_created_groups_count(self, obj):
        return Group.objects.filter(created_by=obj).count()

    def get_posts_count(self, obj):
        return Post.objects.filter(author=obj).count()
