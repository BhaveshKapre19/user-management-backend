# In serializers.py
from rest_framework import serializers
from .models import CustomUserModel, UserFiles

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ['id', 'username', 'email', 'slug', 'is_disable', 'bio', 'avatar']
        read_only_fields = ['slug']  # Ensures slug is read-only

class UserFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFiles
        fields = ['id', 'owner', 'file', 'allowed_users']



class ShareFileSerializer(serializers.Serializer):
    recipient = serializers.PrimaryKeyRelatedField(queryset=CustomUserModel.objects.all())

    def validate_recipient(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError("You cannot share a file with yourself.")
        return value

    def validate(self, data):
        file_id = self.context['file_id']
        try:
            user_file = UserFiles.objects.get(pk=file_id, owner=self.context['request'].user)
        except UserFiles.DoesNotExist as e:
            raise serializers.ValidationError(
                "File not found or you do not have permission to share it."
            ) from e

        if data['recipient'] in user_file.allowed_users.all():
            raise serializers.ValidationError("This file has already been shared with the recipient.")

        return data
