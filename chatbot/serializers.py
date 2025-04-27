from rest_framework import serializers
from .models import CustomUser
from .models import UploadedFile

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Hash password before saving
        user.save()
        print(user)
        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

from rest_framework import serializers
from .models import UploadedFile

class FileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        uploaded_file = UploadedFile()
        uploaded_file.file.put(validated_data["file"], filename=validated_data["file"].name)  # Save to GridFS
        uploaded_file.save()
        return uploaded_file




