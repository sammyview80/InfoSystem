from django.urls import path, include

from .views import UserRegistrationView, UserLoginView, UserDetailView, UserUpdateView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('detail/', UserDetailView.as_view(), name='user-detail'),
    path('update/', UserUpdateView.as_view(), name='user-update'),
    path('api-auth/', include('rest_framework.urls'))
]
