from datetime import datetime, timedelta
from typing import List, Dict, Union
from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.sagan import Result, DnsResult
import pydash as _
import pycountry
from ipwhois import IPWhois
from .probes_db import probes_data
import concurrent.futures

STOPPED: int = 4


def compute_average(x: List[float]) -> float:
    """
    Given a list of floats, returns the average of the list.

    Args:
        x (List[float]): A list of floats.

    Returns:
        float: The average of the list.
    """
    if len(x) == 0:
        return 0
    return round(sum(x) / len(x), 1)


def convert_two_letter_to_three_letter_code(
    two_letter_code: str,
) -> Union[str, None]:
    """
    Given a two-letter country code, returns the corresponding three-letter country code.

    Args:
        two_letter_code (str): A two-letter country code.

    Returns:
        Union[str, None]: The corresponding three-letter country code, or None if the code is invalid.
    """
    try:
        country = pycountry.countries.get(alpha_2=two_letter_code)
        if country:
            return country.alpha_3
        else:
            return None
    except LookupError:
        return None


def compute_average_by_country(results):
    result_by_country = (
        _.chain(
            _.group_by(
                [
                    {
                        "rtt_result": compute_average(
                            [res for res in result["rtt_results"] if res]
                        ),
                        "country": result["geolocation"]["country_code"],
                    }
                    for result in results
                ],
                "country",
            )
        )
        .map_keys(
            lambda value, key: convert_two_letter_to_three_letter_code(key)
        )
        .map_values(
            lambda results, key: compute_average(
                [item["rtt_result"] for item in results if item["rtt_result"]]
            )
        )
        .value()
    )
    return result_by_country


def prepare_results_for_frontend(results):
    return {
        "data": results,
        "min": min(list(results.values()) + [0]),
        "max": max(list(results.values()) + [0]),
        "average": compute_average(results.values()),
    }


def convert_to_timestamp(date_str, delta_days=0):
    dt_object = datetime.strptime(date_str, "%Y-%m-%d")
    dt_object += timedelta(days=delta_days)
    return int(dt_object.timestamp())


def get_probes_ids_list_by_country(country):
    return [
        str(item["id"])
        for item in probes_data
        if item["country_code"] == country
    ]


def check_dns_measurements(
    date,
):
    country_by_probe_id = {
        probe["id"]: probe["country_code"]
        for probe in probes_data
        if probe["country_code"] != None
    }
    params = {
        "start": convert_to_timestamp(date),
        # start date of measurements as unix timestamp
        "stop": convert_to_timestamp(date, delta_days=1),
        # tommorow date of measurements as unix timestamp
    }
    url_path = f"/api/v2/measurements/10209/results"
    # this is url of recurrent DNS measurements  done by RIPE Atlas
    is_success, response_results = AtlasRequest(**{"url_path": url_path}).get(
        **params
    )
    results = (
        _.chain(response_results)
        .map(
            lambda probe_dns_result: {
                "probe_id": probe_dns_result["prb_id"],
                "rtt_results": probe_dns_result.get("result", {}).get(
                    "rt", -1
                ),
            }
        )
        # select only relevant fields from response
        # in case if there is no result ( error during request), set rtt_result to -1
        .group_by("probe_id")
        .map_values(
            lambda value, key: {
                "rtt_result": compute_average(
                    [
                        item["rtt_results"]
                        for item in value
                        if item["rtt_results"] != (-1)
                    ]
                ),
                "country_code": convert_two_letter_to_three_letter_code(
                    country_by_probe_id.get(key)
                ),
            }
        )
        # we compute average rtt for each probe and its 3-letter country code
        .values()
        .group_by("country_code")
        .map_values(
            lambda value: compute_average(
                [item["rtt_result"] for item in value]
            )
        )
        # we compute average rtt for each country
        .omit([None])
        # we remove None keys values
        .value()
    )

    return results


# IPv6 functions


def probes_ipv6_check(probe, start_date, finish_date):
    filters = {
        "probe": probe,
        "date__gte": start_date,
        "date__lte": finish_date,
    }
    url_path = "/api/v2/probes/archive"
    is_success, response = AtlasRequest(**{"url_path": url_path}).get(
        **filters
    )
    if is_success:
        return [
            {
                "id": result["id"],
                "asn_v6": result["asn_v6"],
                "asn_v4": result["asn_v4"],
                "date": result["date"],
            }
            for result in response["results"]
        ]
    else:
        return None


def get_probes_for_country(country_code):
    filters = {"country_code": country_code}
    url_path = "/api/v2/probes/"
    is_success, response = AtlasRequest(**{"url_path": url_path}).get(
        **filters
    )
    if is_success:
        return response["results"]
    else:
        return None


def add_results_ipv6(data, day, percentage):
    if percentage != 0:
        data.append({"name": day, "ipv6": percentage})
    else:
        print()
    return data


def check_as_for_probes(country_code, start_date, finish_date):
    probes = get_probes_for_country(country_code)
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(finish_date, "%Y-%m-%d")
    delta = end_datetime - start_datetime
    ids = [item["id"] for item in probes]
    results = probes_ipv6_check(ids, start_date, finish_date)
    data = []
    for i in range(delta.days + 1):
        current_date = start_datetime + timedelta(days=i)
        # date_obj = datetime.strptime(current_date, "%Y%m%d")
        current_day = current_date.strftime("%Y%m%d")
        as_version_6 = set()
        as_version_4 = set()
        for res in results:
            if res["date"] == current_day:
                if res["asn_v6"] == None:
                    as_version_4.add(res["asn_v4"])
                else:
                    as_version_6.add(res["asn_v6"])
        amount_as_ipv6 = len(as_version_6)
        amount_as_ipv4 = len(as_version_4)
        # print(amount_as_ipv4, "ipv4")
        # print(amount_as_ipv6, "ipv6")
        percentage = (
            (amount_as_ipv6 / (amount_as_ipv6 + amount_as_ipv4)) * 100
            if amount_as_ipv6 + amount_as_ipv4 != 0
            else 0
        )
        # ! TODO fix default value
        # print(f"At date {current_day} the percentage of IPv6 ASes in {country_code} is: {percentage}%")
        current_day = current_date.strftime("%Y-%m-%d")
        data = add_results_ipv6(data, current_day, percentage)
    return data
