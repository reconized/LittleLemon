from django.urls import path
from LittleLemonAPI import views

urlpatterns = [
    # Categories endpoints
    path('categories', views.MenuCategoriesView.as_view()),
    path('categories/<int:pk>', views.MenuCategoryDetailView.as_view()),

    # Menu items endpoints
    # path('menu-items', views.MenuItems.as_view()),
    path('menu-items', views.MenuItemListCreateView.as_view()),
    path('menu-items/', views.MenuItemsByCategoryView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),

    # Manager group management endpoints
    path('groups/manager/users', views.ManagerGroupUserListCreateView.as_view()),
    path('groups/manager/users/<int:userId>', views.ManagerGroupUserDeleteView.as_view()),

    # Delivery crew group management endpoints
    path('groups/delivery-crew/users', views.DeliveryGroupUserListCreateView.as_view()),
    path('groups/delivery-crew/users/<int:userId>', views.DeliveryGroupUserDeleteView.as_view()),

    # Cart management endpoints
    path('cart/menu-items', views.CartMenuItemsView.as_view()),

    # Order managemenet endpoints
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.OrderDetailView.as_view()),
]