from rest_framework import serializers
from LittleLemonAPI.models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        read_only_fields = ['category']
        depth = 1

class MenuItemCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'category_name']
        read_only_fields = ['category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class AddUserToManagerGroupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)

    def validate_username(self, value):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")


class AddUserToDeliveryGroupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)

    def validate_username(self, value):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        write_only=True,
        required=False
    )

    menuitem_name = serializers.CharField(write_only=True, required=False)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menuitem_id', 'menuitem_name', 'quantity', 'unit_price', 'price']

    def validate(self, data):
        menuitem = None

        if 'menuitem_id' in data:
            menuitem = data['menuitem_id']
        elif 'menuitem_name' in data:
            try:
                menuitem = MenuItem.objects.get(title__iexact=data['menuitem_name'])
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError({'menuitem_name': 'Menu item not found.'})
        else:
            raise serializers.ValidationError('Either menuitem_id or menuitem_name is required.')
        
        data['menuitem'] = menuitem
        return data
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be a positive integer.')
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        unit_price = menuitem.price

        cart_item, _ = Cart.objects.update_or_create(
            user=user,
            menuitem=menuitem,
            defaults={'quantity': quantity, 'unit_price': unit_price}
        )
        return cart_item
    
    def get_price(self, obj):
        return obj.unit_price * obj.quantity
    
# class OrderItemSerializer(serializers.ModelSerializer):
#     menuitem = serializers.StringRelatedField()

#     class Meta:
#         model = OrderItem
#         fields = ['menuitem', 'quantity', 'unit_price', 'price']

# class OrderSerializer(serializers.ModelSerializer):
#     orderitem_set = OrderItemSerializer(many=True, read_only=True)
#     user = serializers.StringRelatedField()
#     delivery_crew = serializers.StringRelatedField()

#     class Meta:
#         model = Order
#         fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'orderitem_set']

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class MenuItemShortSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'category']


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemShortSerializer()

    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    delivery_crew = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    items = OrderItemSerializer(source='orderitem_set', many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'delivery_crew',
            'status',
            'status_display',
            'total',
            'date',
            'items'
        ]

    def get_customer(self, obj):
        return UserPublicSerializer(obj.user).data

    def get_delivery_crew(self, obj):
        if obj.delivery_crew is None:
            return {"username": "unassigned", "email": "unassigned"}
        return UserPublicSerializer(obj.delivery_crew).data

    def get_status_display(self, obj):
        if obj.delivery_crew is None or obj.status is None:
            return "unassigned"
        return obj.get_status_display()
