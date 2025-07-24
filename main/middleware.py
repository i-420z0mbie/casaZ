from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Import Django and JWT classes inside method to avoid early evaluation
        from django.conf import settings
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import AnonymousUser
        from channels.db import database_sync_to_async
        from rest_framework_simplejwt.tokens import UntypedToken
        import jwt
        from jwt import InvalidTokenError

        User = get_user_model()

        # Extract token from query string: ?token=<jwt>
        qs = parse_qs(scope.get('query_string', b'').decode())
        token_list = qs.get('token')
        if token_list:
            token = token_list[0]
            try:

                UntypedToken(token)
                # Decode to get user_id
                decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await database_sync_to_async(User.objects.get)(id=decoded_data.get('user_id'))
                scope['user'] = user
            except (InvalidTokenError, KeyError, User.DoesNotExist):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
