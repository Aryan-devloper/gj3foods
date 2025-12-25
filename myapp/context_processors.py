from myapp.models import AdminOwner 


def admin_user(request):
    admin_id = request.session.get('admin_id')
    user = None
    if admin_id:
        try:
            user = AdminOwner.objects.get(pk=admin_id)
        except AdminOwner.DoesNotExist:
            pass
    return {'admin_user': user}


from .models import Cart, Registration

def cart_item_count(request):
    user_id = request.session.get('user_id')
    count = 0
    if user_id:
        try:
            user = Registration.objects.get(id=user_id)
            count = Cart.objects.filter(user=user).count()
        except Registration.DoesNotExist:
            pass
    return {'cart_count': count}

