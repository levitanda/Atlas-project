from django.http import JsonResponse


def dns_data(request):
    return JsonResponse({"hey": "Hello, World!"})
