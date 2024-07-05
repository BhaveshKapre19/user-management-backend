from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserSerializer, UserFilesSerializer, ShareFileSerializer
from .models import CustomUserModel, UserFiles

User = get_user_model()

class HomeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_files = UserFiles.objects.filter(owner=user)
        shared_files = UserFiles.objects.filter(allowed_users=user)
        
        user_files_serializer = UserFilesSerializer(user_files, many=True)
        shared_files_serializer = UserFilesSerializer(shared_files, many=True)
        user_serializer = CustomUserSerializer(user)
        
        return Response({
            'user_files': user_files_serializer.data,
            'shared_files': shared_files_serializer.data,
            'user':user_serializer.data
        })

class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            user.save()
            raw_password = request.data.get('password1')
            if user := authenticate(email=user.email, password=raw_password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({'error': 'Authentication failed. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if user := authenticate(email=email, password=password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful.'
            })
        return Response({'error': 'Invalid credentials. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()  # This assumes you have a token to delete
        return Response({'message': 'Logout successful.'})

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

class ProfileEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFilesListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_files = UserFiles.objects.filter(owner=request.user)
        serializer = UserFilesSerializer(user_files, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = UserFilesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFileDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        user_file = get_object_or_404(UserFiles, pk=pk)
        serializer = UserFilesSerializer(user_file)
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        user_file = get_object_or_404(UserFiles, pk=pk)
        user_file.delete()
        return Response({'message': 'File deleted successfully.'})

class ShareFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        serializer = ShareFileSerializer(data=request.data)
        if serializer.is_valid():
            recipient_user = serializer.validated_data['recipient']
            try:
                file_to_share = UserFiles.objects.get(pk=pk, owner=request.user)
                file_to_share.allowed_users.add(recipient_user)
                return Response({'message': f'File shared with {recipient_user.username} successfully.'})
            except UserFiles.DoesNotExist:
                return Response({'error': 'File not found or you do not have permission to share it.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AutocompleteUsersAPIView(APIView):
    def get(self, request, *args, **kwargs):
        if term := request.GET.get('term', None):
            users = CustomUserModel.objects.filter(username__icontains=term)
            results = [{'label': user.username, 'value': user.username} for user in users]
            return Response(results)
        return Response([])
