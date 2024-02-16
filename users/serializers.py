from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import PromptInput

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user creation, including password validation.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password')

    def validate(self, data):
        """
        Validate user data, including password validation.
        """
        user = User(**data)
        password = data.get('password')

        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            serializer_errors = serializers.as_serializer_error(e)
            raise exceptions.ValidationError(
                {'password': serializer_errors['non_field_errors']}
            )
        return data

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number')

class PromptSerializer(serializers.ModelSerializer):
    """
    Serializer for prompt input.
    """

    class Meta:
        model = PromptInput
        fields = '__all__'

class ProfilePicSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile pictures.
    """

    class Meta:
        model = User
        fields = ('profile',)
