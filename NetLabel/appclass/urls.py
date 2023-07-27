from django.urls import path
from .views import *
urlpatterns = [
    path('index',Message.as_view(),name='index'),
    path('list',Label_List.addtest),
    path('classname',Label_List.add_class),
    path('read',Label_List.readtest),
    path('training',Model_Training.as_view(),name='training'),
    path('training/progress', Model_Training.get_training_progress, name='training/progress'),
    path('Augmentation',Data_Augmentation.as_view(),name='Augmentation'),
    path('Augmentation/action',Data_Augmentation.augment,name='Augmentation/action'),
    path('Augmentation/export',Data_Augmentation.image_label,name='Augmentation/export'),
    path('ModelView',Model_Examine.as_view(),name='ModelView'),
    # path('index/<str:name>/<int:age>',index),
]
