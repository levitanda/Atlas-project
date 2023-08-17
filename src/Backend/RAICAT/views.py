from django.http import JsonResponse
from .utils import (
    check_dns_measurements,
    compute_ipv6_percentage,
    prepare_results_for_frontend,
    compute_dns_between_dates,
    convert_to_timestamp,
    compute_fragmented_data,
    compute_ipv6_percentage_between_dates_for_country_list
)
from .dns_countries_data import countries_data
from .ipv6_cached_data import countries_ipv6
import json

def dns_data(request, date):
    dns_result = prepare_results_for_frontend(check_dns_measurements(date))
    return JsonResponse(dns_result)


def dns_data_line(request, start_date, end_date):
    result = compute_fragmented_data(
        start_date, end_date, countries_data, compute_dns_between_dates
    )

    return JsonResponse({"data": result})


def ipv6_data(request, countries, first_date, second_date):
    countries_list = json.loads(countries)
    print(first_date)
    data = compute_fragmented_data(first_date, second_date, countries_ipv6, (lambda start, end: compute_ipv6_percentage_between_dates_for_country_list(countries_list, start, end)))
    return JsonResponse({"data": data})
