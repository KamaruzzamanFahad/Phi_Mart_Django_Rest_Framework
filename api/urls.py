from django.urls import path, include
# from rest_framework.routers import SimpleRouter, DefaultRouter
from product.views import ProductViewSet, CategoryViewSet, ReviewViewSet, ProductImageViewSet
from rest_framework_nested import routers
from order.views import CartViewSet, CartItemViewSet, OrderViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="PhiMart Ecom API",
      default_version='v1',
      description="api description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('categorys', CategoryViewSet)
router.register('carts', CartViewSet, basename='carts')
router.register('orders', OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', ReviewViewSet, basename='product-reviews')
product_router.register('images', ProductImageViewSet, basename='product-images')

cart_item_rout = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_item_rout.register('items', CartItemViewSet, basename='cart-item')


urlpatterns = [
    
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_item_rout.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # path('products/', include('product.products_urls')),
    # path('categorys/', include('product.category_urls')),
    
]

