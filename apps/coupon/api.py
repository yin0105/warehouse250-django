from django.http import JsonResponse

from .models import Coupon

def api_can_use(request):
    print(" ** api_can_use ** ")
    json_response = {}
    coupon_code = request.GET.get('coupon_code', '')
    print("coupon_code = ", coupon_code)

    try:
        coupon = Coupon.objects.get(code=coupon_code)

        if coupon.can_use():
            json_response = {'amount': coupon.discount}
        else:
            json_response = {'amount': 0}
    except Exception:
        json_response = {'amount': 0}

    return JsonResponse(json_response)
