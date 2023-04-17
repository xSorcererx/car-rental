from django.contrib.auth import password_validation as validators
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import exceptions
from django.utils.encoding import (DjangoUnicodeDecodeError, force_str,
                                   smart_bytes, smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from requests import Response
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serialzier for profile, that extends user instance
    """
    
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'country', 'city', 'postal_code',
                  'street', 'apartment_number', 'phone_number')
        

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for user that serialize "url", "username", "email",
    "password", "password2" and relation to profile serializer
    """
    
    url = serializers.HyperlinkedIdentityField(view_name="users-detail")
    profile = ProfileSerializer()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        # required set to false, to allow update wuthout password field
        # password existance is being checked in create method
        required=False,
        )
    password2 = serializers.CharField(
        label='Confirm password', 
        write_only=True,
        style={'input_type': 'password'},
        required=False,
        )
    
    class Meta:
        model = User
        fields = ('url', 'username', "email", "password", "password2", 
                  'profile')
        
    def validate_password2(self, value):
        """
        Checks if password2 is the same as password
        """
        data = self.get_initial()
        password = data.get('password')
        password2 = value
        if password != password2:
            raise ValidationError('Passwords must match')
        return super(UserSerializer, self).validate(value)
        
    def validate_password(self, value):
        """
        Validates password by django validators
        """
        password = value
        errors = dict()
        try:
            validators.validate_password(password=password)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
            if errors:
                raise serializers.ValidationError(errors)
        return super(UserSerializer, self).validate(value)
    
    def create(self, validated_data):
        """
        Creates user and related profile instance
        """
        profile_data = validated_data.pop('profile')
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        # required set to false in password field so need to check here
        if 'password' not in validated_data:
            raise ValidationError(
                {"password": "This field may not be blank."})
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user, **profile_data)
        return user
    
    def update(self, instance, validated_data):
        nested_serializer = self.fields['profile']
        nested_instance = instance.profile
        nested_data = validated_data.pop('profile')
        nested_serializer.update(nested_instance, nested_data)
        if 'password' in validated_data:
            validated_data.pop('password')

        return super(UserSerializer, self).update(instance, validated_data)
      

class EmailVerificationSerializer(serializers.ModelSerializer):
    """
    serializer used to verify account by email
    """
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']
        

class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    serializer to enable changing password
    """
    password1 = serializers.CharField(
        write_only=True, 
        required=True,
        )
    password2 = serializers.CharField(
        write_only=True, 
        required=True
        )
    old_password = serializers.CharField(
        write_only=True, 
        required=True
        )

    class Meta:
        model = User
        fields = ('old_password', 'password1', 'password2')

    def validate(self, attrs):
        """
        checks if password2 is the same as password1
        """
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password1': "password fields dont match !"})
        return attrs
    
    def validate_password1(self, value):
        """
        Validates password by django validators
        """
        password = value
        errors = dict()
        try:
            validators.validate_password(password=password)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
            if errors:
                raise serializers.ValidationError(errors)
        return super(ChangePasswordSerializer, self).validate(value)

    def validate_old_password(self, value):
        """
        Checks if old password is correct
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct !"})
        return value
    
    def update(self, instance, validated_data):
        """
        Overrides update method
        """
        user = self.context['request'].user
        if user.pk != instance.pk:
            raise serializers.ValidationError(
                {"authorize": "You dont have permission for this user !"})

        instance.set_password(validated_data['password1'])
        instance.save()
        return instance
    

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    """
    Serializer to enter email to reset password
    """
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer to set new password
    """
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                # raise AuthenticationFailed('The reset link is invalid', 401)
                return Response({'message':'Link invalid'}, status=status.HTTP_200_OK)
            


            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            return Response({'message':'Link invalid'}, status=status.HTTP_200_OK)

            # raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
                

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, value):
        self.token = value['refresh']
        return value

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
