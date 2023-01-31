from django.urls import path
from .views import Message,Label_List
urlpatterns = [
    path('index2',Message.as_view()),
    path('list',Label_List.addtest),
    path('read',Label_List.readtest),
    # path('index/<str:name>/<int:age>',index),
]
