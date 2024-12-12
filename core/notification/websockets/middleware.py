from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
import urllib.parse


class TokenAuthMiddleware(BaseMiddleware):
    @database_sync_to_async
    def get_user(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()

    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        params = urllib.parse.parse_qs(query_string)
        token_key = params.get('token', [None])[0]

        scope['user'] = await self.get_user(token_key) if token_key else AnonymousUser()
        return await super().__call__(scope, receive, send)
