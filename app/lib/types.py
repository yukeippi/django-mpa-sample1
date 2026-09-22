from django.contrib.auth.models import User
from django.http import HttpRequest


# @login_requiredを通過したビューのリクエスト。
# 素のHttpRequestではuserがAnonymousUserを含む型になるため、認証済みであることを型で表す
class AuthenticatedHttpRequest(HttpRequest):
    user: User
