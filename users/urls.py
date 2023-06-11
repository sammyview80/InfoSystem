from django.urls import path, include

from .views import UserRegistrationView, UserLoginView, UserDetailView, UserUpdateView, FetchMailView, TokenView, GmailOauthView, OauthLink, CatchOauthCreds, ExtraceSheet

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('detail/', UserDetailView.as_view(), name='user-detail'),
    path('update/', UserUpdateView.as_view(), name='user-update'),
    path('fetchmail/', FetchMailView.as_view(), name='fetch-mail'),
    path('tokens/', TokenView.as_view(), name='token'),
    path('api-auth/', include('rest_framework.urls')),
    path('gmailoauth/', GmailOauthView.as_view(), name='gmail-oauth'),
    path('oauthlink/', OauthLink.as_view(), name='oauth-link'),
    path('oauth2callback/', CatchOauthCreds.as_view(), name='oauth-link-catch'),
    path('extract/',  ExtraceSheet.as_view(), name='extradt')
]
