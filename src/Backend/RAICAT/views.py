from django.http import JsonResponse
from .utils import check_dns_measurements


def dns_data(request, first_date, second_date):
    if first_date == second_date:
        results = check_dns_measurements(first_date)
        return JsonResponse(
            {
                "first_date": results,
            }
        )
    else:
        return JsonResponse(
            {
                "first_date": check_dns_measurements(first_date),
                "second_date": check_dns_measurements(second_date),
            }
        )
