from rest_framework import serializers
from decimal import Decimal
from product.models import Category, Product, Review, ProductImage
from users.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count']
    product_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price')
    description = serializers.CharField(max_length=100)
    image = serializers.ImageField()
    price_with_tax = serializers.SerializerMethodField(method_name='get_price_with_tax')
    category_byid = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    category_byname = serializers.StringRelatedField(source='category')
    category_byserializer = CategorySerializer(source='category')
    category = serializers.HyperlinkedRelatedField(
        view_name='view_category',
        lookup_field='pk',
        read_only=True
    )

    def get_price_with_tax(self, product):
        return round(product.price * Decimal('1.15'), 2)


class ProductImageSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ProductImage
        fields = ['id', 'image']



class ProductModelSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'description', 'images', 'price_with_tax', 'category_byid', 'category_byname', 'category_byserializer', 'category_byhyperlink']
    
    category_byid = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    category_byname = serializers.StringRelatedField(source='category', read_only=True)
    category_byserializer = CategorySerializer(source='category', read_only=True)
    category_byhyperlink = serializers.HyperlinkedRelatedField(
        source='category',
        view_name='category-detail',
        lookup_field='pk',
        read_only=True
    )
    price_with_tax = serializers.SerializerMethodField(method_name='get_price_with_tax')
    def get_price_with_tax(self, product):
        return round(product.price * Decimal('1.15'), 2)

    def validate_price(self, price):
        if price < 0:
            raise serializers.ValidationError("Price cannot be negative")
        if price > 1000000:
            raise serializers.ValidationError("Price cannot be greater than 1000000")
        return price

    
    # object lavel validations
    # def validate(self, attrs):
    #     if attrs['price'] < 0:
    #         raise serializers.ValidationError("Price cannot be negative")
    #     if attrs['price'] > 1000000:
    #         raise serializers.ValidationError("Price cannot be greater than 1000000")
    #     return attrs

    # create method override
    # def create(self, validated_data):
    #     product = Product.objects.create(**validated_data)
    #     product.others = 1 # this is dummy data for testing
    #     product.save()
    #     return product



class ReviewUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model = User
        fields = ['id', 'name']

    def get_current_user_name(salf,obj):
        return obj.get_full_name()
        

    

class ReviewSerializer(serializers.ModelSerializer):
    # user = ReviewUserSerializer()
    user = serializers.SerializerMethodField(method_name='get_user')

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rattings', 'comment']
        read_only_fields = ['user', 'product']

    def get_user(self, obj):
        return ReviewUserSerializer(obj.user).data

        

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)