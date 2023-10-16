from django.urls import path
from .views import Register,Login,LogoutUser,A,B

urlpatterns = [
    path('',Login.as_view(),name='login'),
    path('login',Login.as_view(),name='login'),
    path('register',Register.as_view(),name='register'),
    # path('index',Index.as_view(),name='index'),#name的用意，是當view中的函數使用 redirect(reverse('login')) 時 reverse中需引用的值
    path('logout',LogoutUser.as_view(),name='logout'),
    # path('a',A.as_view(),name='a_page'),
    # path('b',B.as_view(),name='b_page'),
]
