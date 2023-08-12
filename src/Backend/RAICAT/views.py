from django.http import JsonResponse
from .utils import (
    check_dns_measurements,
    compute_ipv6_percentage,
    prepare_results_for_frontend,
    compute_dns_between_dates,
    compute_fragmented_data,
)
from .dns_countries_data import countries_data


def dns_data(request, date):
    dns_result = prepare_results_for_frontend(check_dns_measurements(date))
    return JsonResponse(dns_result)


def dns_data_line(request, start_date, end_date):
    result = compute_fragmented_data(
        start_date, end_date, countries_data, compute_dns_between_dates
    )

    return JsonResponse({"data": result})


def ipv6_data(request, country, first_date, second_date):
    ipv6_result = compute_ipv6_percentage(
        country,
        first_date,
        second_date,
    )
    return JsonResponse({"data": ipv6_result})
