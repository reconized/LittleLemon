from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated
from LittleLemonAPI.models import MenuItem
from LittleLemonAPI.serializers import MenuItemSerializer, CategorySerializer, UserSerializer, \
        AddUserToManagerGroupSerializer, AddUserToDeliveryGroupSerializer, CartSerializer, \
        MenuItemCategorySerializer, OrderSerializer, OrderItemSerializer
from LittleLemonAPI.models import Category, Cart, Order, OrderItem
from LittleLemonAPI.permissions import IsManagerOrReadOnly, IsManager, IsDeliveryCrew, IsCustomer
from django.contrib.auth.models import User, Group
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import PermissionDenied

def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

# Create your views here.
class MenuCategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManager]

class MenuCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]

class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    ordering_fields = ['title', 'price', 'featured']
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save()

    
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='manager').exists():
            return Response({'detail', 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='manager').exists():
            return Response({'detail', 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='manager').exists():
            return Response({'detail', 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
class MenuItemsByCategoryView(generics.ListAPIView):
    serializer_class = MenuItemCategorySerializer

    def get_queryset(self):
        queryset = MenuItem.objects.all()

        category_name = self.request.query_params.get('category', None)

        if category_name:
            queryset = queryset.filter(category__title__iexact=category_name)
        
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        category_name = self.request.query_params.get('category', None)
        if category_name and not queryset.exists():
            return Response(
                {'detail': f"No menu items found for category: '{category_name}' or category does not exist."}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.data)

class ManagerGroupUserListCreateView(generics.GenericAPIView):
    serializer_class = AddUserToManagerGroupSerializer
    permission_classes = [IsManagerOrReadOnly]
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            group = Group.objects.get(name='manager')
        except Group.DoesNotExist:
            return Response({'detail': 'Manager group does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']

        with transaction.atomic():
            group, _ = Group.objects.get_or_create(name='manager')

            if group.user_set.filter(pk=user.pk).exists():
                return Response({'detail': f'User {user.username} is already in the Manager group'},
                                status=status.HTTP_409_CONFLICT)
            
            group.user_set.add(user)
            return Response({'detail': f'User {user.username} added to Manager group.'}, status=status.HTTP_201_CREATED)
    
class ManagerGroupUserDeleteView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def get(self, request, userId, *args, **kwargs):
        return Response({'detail': 'This endpoint only supports DELETE.'}, status=status.HTTP_200_OK)

    def delete(self, request, userId, *args, **kwargs):
        try:
            user = User.objects.get(pk=userId)
            group = Group.objects.get(name='manager')
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'detail': 'Manager group does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        if not group.user_set.filter(pk=user.pk).exists():
            return Response({'detail': f'User {user.username} is not found in the group.'}, status=status.HTTP_404_NOT_FOUND)
        
        group.user_set.remove(user)
        return Response({'detail': f'User {user.username} removed from Manager group.'}, status=status.HTTP_200_OK)
    
class DeliveryGroupUserListCreateView(generics.GenericAPIView):
    serializer_class = AddUserToDeliveryGroupSerializer
    permission_classes = [IsManagerOrReadOnly]
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            group = Group.objects.get(name='delivery-crew')
        except Group.DoesNotExist:
            return Response({'detail': 'Delivery group does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        users = group.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']

        with transaction.atomic():
            group, _ = Group.objects.get_or_create(name='delivery-crew')
            if group.user_set.filter(pk=user.pk).exists():
                return Response({'detail': f'User {user.username} is already in the Delivery group.'},
                                status=status.HTTP_409_CONFLICT)
            
            group.user_set.add(user)
                
            return Response({'detail': f'User {user.username} added to Delivery group.'}, status=status.HTTP_201_CREATED)
    
class DeliveryGroupUserDeleteView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    def delete(self, request, userId, *args, **kwargs):
        try:
            user = User.objects.get(pk=userId)
            group = Group.objects.get(name='delivery-crew')
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'detail': 'Delivery group does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        group.user_set.remove(user)
        return Response({'detail': f'User {user.username} removed from Delivery group.'}, status=status.HTTP_200_OK)
    
    def get(self, request, userId, *args, **kwargs):
        return Response({'detail': 'This endpoint only supports DELETE.'}, status=status.HTTP_200_OK)
    
class CartMenuItemsView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = self.get_serializer(cart_items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        with transaction.atomic():
            if serializer.is_valid():
                cart_item = serializer.save()
                return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        deleted_count, _ = Cart.objects.filter(user=request.user).delete()
        return Response({'message': f'Deleted {deleted_count} cart item(s).'}, status=status.HTTP_204_NO_CONTENT)

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['delivery_crew__username', 'status']
    ordering_fields = ['date', 'total']
    pagination_class = None 

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            return Order.objects.all()
        elif user.groups.filter(name="delivery-crew").exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.unit_price * item.quantity for item in cart_items)
        order = Order.objects.create(user=user, total=total, status=None)

        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.unit_price * item.quantity
            ) for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        cart_items.delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.all()

    def get_object(self):
        order = super().get_object()
        user = self.request.user

        if user.groups.filter(name="manager").exists():
            return order
        elif user.groups.filter(name="delivery-crew").exists():
            if order.delivery_crew == user:
                return order
            else:
                self.permission_denied(self.request)
        else:
            if order.user == user:
                return order
            else:
                self.permission_denied(self.request)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        data = request.data

        def is_unassigned(value):
            return isinstance(value, str) and value.strip().lower() == "unassigned"

        if user.groups.filter(name="manager").exists():
            if 'delivery_crew' in data:
                if is_unassigned(data['delivery_crew']):
                    order.delivery_crew = None
                    order.status = None
                else:
                    try:
                        crew_user = User.objects.get(username=data['delivery_crew'])
                        if not crew_user.groups.filter(name="delivery-crew").exists():
                            return Response({'error': 'User is not delivery crew.'}, status=400)
                        order.delivery_crew = crew_user
                    except User.DoesNotExist:
                        return Response({'error': 'User not found.'}, status=404)

            if 'status' in data:
                status_value = data['status']
                if is_unassigned(status_value):
                    order.delivery_crew = None
                    order.status = None
                elif str(status_value) in ['0', '1']:
                    order.status = int(status_value)
                else:
                    return Response({'error': 'Invalid status value.'}, status=400)

            order.save()
            return Response(OrderSerializer(order).data)

        elif user.groups.filter(name="delivery-crew").exists():
            if order.delivery_crew != user:
                return Response({"error": "Not assigned to this order."}, status=403)
            if 'status' in data and str(data['status']) in ['0', '1']:
                order.status = int(data['status'])
                order.save()
                return Response(OrderSerializer(order).data)
            else:
                return Response({'error': 'Invalid or missing status.'}, status=400)

        return Response({"error": "Unauthorized."}, status=403)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)  # Delegate to patch for logic reuse

    def delete(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            return Response({'error': 'Only managers can delete orders.'}, status=403)
        return super().delete(request, *args, **kwargs)
