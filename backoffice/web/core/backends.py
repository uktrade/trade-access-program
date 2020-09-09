from authbroker_client.backends import AuthbrokerBackend


class CustomAuthbrokerBackend(AuthbrokerBackend):

    def user_create_mapping(self, profile):
        return {
            'is_active': True,
            'first_name': profile['first_name'],
            'last_name': profile['last_name'],
            'email': profile['email'],
        }
