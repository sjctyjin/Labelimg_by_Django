from django.urls import path
from .views import Index
urlpatterns = [
    path('index',Index.as_view()),
    # path('index/<str:name>/<int:age>',index),
]
