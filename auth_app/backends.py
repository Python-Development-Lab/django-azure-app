from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


class EntraIDBackend(BaseBackend):
    """Custom authentication backend for Microsoft Entra ID."""

    def authenticate(self, request, entra_id_claims=None, **kwargs):
        if not entra_id_claims:
            return None

        oid = entra_id_claims.get('oid') or entra_id_claims.get('sub')
        if not oid:
            return None

        email = entra_id_claims.get('preferred_username', '')
        full_name = entra_id_claims.get('name', '')
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user, created = User.objects.get_or_create(
            username=oid,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        if not created:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save(update_fields=['email', 'first_name', 'last_name'])

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
