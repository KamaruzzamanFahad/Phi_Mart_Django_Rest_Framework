from django.urls import path
from product import views

urlpatterns = [
    path('', views.ViewProductWithGeneric.as_view(), name='view_product'),
    path('<int:id>', views.ViewSpecificProductWithGeneric.as_view(), name='view_specific_product') 
] 