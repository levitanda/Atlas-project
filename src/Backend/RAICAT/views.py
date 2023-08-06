from django.http import JsonResponse
from .utils import (
    check_dns_measurements,
    check_as_for_probes,
    prepare_results_for_frontend,
    dns_between_dates,
    convert_to_timestamp,
)
from .dns_countries_data import countries_data


def dns_data(request, date):
    dns_result = prepare_results_for_frontend(check_dns_measurements(date))
    return JsonResponse(dns_result)


def dns_data_line(request, start_date, end_date):
    start_date_timestamp = convert_to_timestamp(start_date)
    end_date_timestamp = convert_to_timestamp(end_date)
    last_day_in_cache = countries_data[-1]["name"]
    first_date_in_cache = countries_data[0]["name"]
    (
        first_date_in_cache_timestamp,
        last_day_in_cache_timestamp,
        cached_dates,
    ) = (
        convert_to_timestamp(first_date_in_cache),
        convert_to_timestamp(last_day_in_cache),
        [item["name"] for item in countries_data],
    )
    if (
        start_date_timestamp >= first_date_in_cache_timestamp
        and start_date_timestamp <= last_day_in_cache_timestamp
    ):
        start_index = cached_dates.index(start_date)
        if end_date_timestamp <= last_day_in_cache_timestamp:
            end_index = cached_dates.index(end_date)
            return JsonResponse(
                {"data": countries_data[start_index : end_index + 1]}
            )
        else:
            # end_date > last_day_in_cache_timestamp
            result = countries_data[start_index:]
            result.extend(dns_between_dates(last_day_in_cache, end_date)[1:])
            return JsonResponse({"data": result})
    elif (
        start_date_timestamp < first_date_in_cache_timestamp
        and end_date_timestamp >= first_date_in_cache_timestamp
        and end_date_timestamp <= last_day_in_cache_timestamp
    ):
        # start_date < first_date_in_cache_timestamp
        if end_date_timestamp <= last_day_in_cache_timestamp:
            end_index = cached_dates.index(end_date)
            result = dns_between_dates(start_date, first_date_in_cache)
            result.extend(countries_data[1 : end_index + 1])
            return JsonResponse({"data": result})
        else:
            # end_date > last_day_in_cache_timestamp
            result = dns_between_dates(start_date, first_date_in_cache)
            result.extend(countries_data[1:-1])
            result.extend(dns_between_dates(last_day_in_cache, end_date))
            return JsonResponse({"data": result})
    else:
        return JsonResponse({"data": dns_between_dates(start_date, end_date)})


def ipv6_data(request, country, first_date, second_date):
    ipv6_result = check_as_for_probes(country, first_date, second_date)
    return JsonResponse({"data": ipv6_result})
