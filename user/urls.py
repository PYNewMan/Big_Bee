from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$',views.Users.as_view()),
    url(r'^/activation',views.users_active),
    url(r'^/weibo/authorization$',
        views.OAuthWeiboUrlView.as_view()),
    url(r'^/weibo/users$',
        views.OAuthWeiboView.as_view())
]








