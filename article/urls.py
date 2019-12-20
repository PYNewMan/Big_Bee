from django.conf.urls import include, url
from . import views
urlpatterns = [
    url(r'^/detail' ,views.Article.as_view()),
]



