from django.urls import path
from . import views


urlpatterns = [
    path('a/', views.index), 
    #여기서 path 다음에 키고 키에따라서 뒤에url이 불러와짐 그래서 앞에 키설정 잘해줘야하고, 뒤에 views는 여기에 있는 index함수를 불러온다는뜻 
]
