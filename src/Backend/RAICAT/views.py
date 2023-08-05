from django.http import JsonResponse
from .utils import (
    check_dns_measurements,
    check_as_for_probes,
)


def dns_data(request, first_date, second_date):
    if first_date == second_date:
        dns_result = check_dns_measurements(first_date)
        return JsonResponse(
            {
                "result1": dns_result,
                "result2": dns_result,
            }
        )
    else:
        return JsonResponse(
            {
                "result1": check_dns_measurements(first_date),
                "result2": check_dns_measurements(second_date),
            }
        )


def ipv6_data(request, country, first_date, second_date):
    ipv6_result = check_as_for_probes(country, first_date, second_date)
    return JsonResponse({"data": ipv6_result})
