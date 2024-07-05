from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    ProfileEditAPIView,
    UserFilesListAPIView,
    UserFileDetailAPIView,
    ShareFileAPIView,
    AutocompleteUsersAPIView,
    ShareFileAPIView,
    HomeAPIView
)

urlpatterns = [
    path('home/', HomeAPIView.as_view(), name='home'),
    path('register/', RegisterAPIView.as_view(), name='register_api'),
    path('login/', LoginAPIView.as_view(), name='login_api'),
    path('logout/', LogoutAPIView.as_view(), name='logout_api'),
    path('profile/', ProfileAPIView.as_view(), name='profile_api'),
    path('profile/edit/', ProfileEditAPIView.as_view(), name='profile_edit_api'),
    path('user/files/', UserFilesListAPIView.as_view(), name='user_files_api'),
    path('user/files/<int:pk>/', UserFileDetailAPIView.as_view(), name='user_file_detail_api'),
    path('user/files/share/<int:pk>/', ShareFileAPIView.as_view(), name='share_file_api'),
    path('autocomplete/users/', AutocompleteUsersAPIView.as_view(), name='autocomplete_users_api'),
    path('user/files/share/<int:file_id>/', ShareFileAPIView.as_view(), name='user_file_share_api'),
]
