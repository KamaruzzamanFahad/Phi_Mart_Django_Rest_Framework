from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from product.models import Product, Category, Review, ProductImage
from product.serializer import ProductSerializer, CategorySerializer, ProductModelSerializer, ReviewSerializer, ProductImageSerializer
from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend # must install django-filter
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination # this is default paginations by rest framework
from product.paginstions import ProductPagination # this is custom paginations by creating pagination class
from rest_framework.permissions import IsAdminUser, AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
from api.permissitions import IsAdminOrReadOnly,FullDjangoModelPermissition
from product.permissitions import IsReviewAuthorOrReadOnly


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['category_id'] direct filter
    filterset_class = ProductFilter # custom filter by filter class
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'stock']
    # pagination_class = PageNumberPagination # this one way to add pagination by adding in settings.py for all api
    pagination_class = ProductPagination 

    # def get_queryset(self):
    #     queryset = Product.objects.select_related('category').all() 
    #     category_id = self.request.query_params.get('category_id')
    #     if category_id:
    #         queryset = queryset.filter(category_id=category_id)
    #     return queryset
    
    serializer_class = ProductModelSerializer

    # permission_classes =[IsAdminOrReadOnly]
    # permission_classes =[DjangoModelPermissions]
    # permission_classes =[DjangoModelPermissionsOrAnonReadOnly]
    # permission_classes =[FullDjangoModelPermissition]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()]

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes =[IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id = self.kwargs['product_pk'])
    
    def perform_create(self, serializer):
        serializer.save(product_id = self.kwargs['product_pk'])


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer

class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes =[IsReviewAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
        
        




@api_view(['GET', 'POST'])
def view_product(request):
    if request.method == 'GET':
        serializer = ProductModelSerializer(Product.objects.select_related('category').all(), many=True, context={'request': request})
        return Response({
            "products": serializer.data
        })
    elif request.method == 'POST':
        serializer = ProductModelSerializer(data=request.data, context={'request': request})
        # if 
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewProduct(APIView):

    def get(self, request):
        serializer = ProductModelSerializer(Product.objects.select_related('category').all(), many=True, context={'request': request})
        return Response({
            "products": serializer.data
        })
    
    def post(self, request):
        serializer = ProductModelSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ViewProductWithGeneric(ListCreateAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductModelSerializer
    
    # def get_queryset(self):
    #     return Product.objects.select_related('category').all()

    # def get_serializer_class(self):
    #     return ProductModelSerializer

    # def get_serializer_context(self):
    #     return {'request': self.request}




@api_view(['GET', 'PUT', 'DELETE'])
def view_specific_product(request, id):
    if request.method == 'GET':
        serializer = ProductModelSerializer(get_object_or_404(Product, id=id), context={'request': request})
        return Response({
        "product": serializer.data
        })
    elif request.method == 'PUT':
        product = get_object_or_404(Product, id=id)
        serializer = ProductModelSerializer(product, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        product = get_object_or_404(Product, id=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        


class ViewSpecificProduct(APIView):

    def get(self, request, id):
        serializer = ProductModelSerializer(get_object_or_404(Product, id=id), context={'request': request})
        return Response({
        "product": serializer.data
        })
    
    def put(self,request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductModelSerializer(product, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ViewSpecificProductWithGeneric(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductModelSerializer
    lookup_field = 'id'


@api_view(['GET'])
def view_category(request):
    serializer = CategorySerializer(Category.objects.annotate(product_count=Count('products')).all(), many=True)
    return Response({
        "categories": serializer.data
    })


@api_view(['GET'])
def view_specific_category(request, pk):
    serializer = CategorySerializer(get_object_or_404(Category, pk=pk))
    return Response({
        "category": serializer.data
    })
    

class ViewSpecificCategory(APIView):
    def get(self, request, pk):
        serializer = CategorySerializer(Category.objects.annotate(product_count=Count('products')).filter(pk=pk), many=True)
        return Response({
            "category": serializer.data
        })
    
    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
