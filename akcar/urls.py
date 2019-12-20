from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^/search' ,views.Akc_Search.as_view()),
    url(r'^/top_five',views.Top_Five.as_view()),
    url(r'^/ck_key',views.Ck_Key.as_view()),
    url(r'^/like_car',views.Like_Car.as_view()),
]


