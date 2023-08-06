from django.http import JsonResponse
from .utils import (
    check_dns_measurements,
    check_as_for_probes,
    prepare_results_for_frontend,
    dns_between_dates,
)
from .dns_countries_data import countries_data


def dns_data(request, date):
    dns_result = prepare_results_for_frontend(check_dns_measurements(date))
    return JsonResponse(dns_result)


def dns_data_line(request, start_date, end_date):
    # return JsonResponse({"data": countries_data})
    return JsonResponse({"data": dns_between_dates(start_date, end_date)})


def ipv6_data(request, country, first_date, second_date):
    ipv6_result = check_as_for_probes(country, first_date, second_date)
    return JsonResponse({"data": ipv6_result})
