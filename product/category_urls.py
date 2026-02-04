from django.urls import path
from product import views

urlpatterns = [
    path('', views.view_category, name='view_category'),
    path('<int:pk>', views.ViewSpecificCategory.as_view(), name='view_category') 
]