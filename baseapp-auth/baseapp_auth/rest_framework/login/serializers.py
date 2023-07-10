from django.contrib.auth import authenticate

from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token

from baseapp_auth.models import User


class LoginPasswordExpirationMixin:
    def check_password_expiration(self, user):
        if user.is_password_expired:
            raise exceptions.AuthenticationFailed(
                {
                    "password": [
                        _(
                            "Your password has expired. Please reset it or contact the administrator."
                        )
                    ]
                }
            )


class LoginSerializer(LoginPasswordExpirationMixin, serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        validated_data = super().validate(data)
        self.user = authenticate(
            username=validated_data["email"],
            password=validated_data["password"],
        )
        if not self.user:
            raise exceptions.AuthenticationFailed(
                detail=_("Unable to login with provided credentials.")
            )
        self.check_password_expiration(self.user)
        return validated_data

    def create(self, validated_data):
        return Token.objects.get_or_create(user=self.user)[0]
