from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class CustomModelBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            print(user.password == password)
            if user.password == password:
                return user
        except User.DoesNotExist:
            pass

        return None
