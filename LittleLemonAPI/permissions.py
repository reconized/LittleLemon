from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.groups.filter(name='manager').exists()
    
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="manager").exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="delivery-crew").exists()

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return not (request.user.groups.filter(name="manager").exists() or 
                    request.user.groups.filter(name="delivery-crew").exists())
    
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
