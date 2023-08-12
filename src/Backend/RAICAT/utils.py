from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional
from ripe.atlas.cousteau import AtlasRequest
import pydash as _
import pycountry
from .probes_db import probes_data


STOPPED: int = 4

NO_RTT_RESULT: int = -1


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

def convert_three_letter_to_two_letter_code(
    three_letter_code: str,
) -> Union[str, None]:
    """
    Given a three-letter country code, returns the corresponding two-letter country code.

    Args:
        three_letter_code (str): A three-letter country code.

    Returns:
        Union[str, None]: The corresponding three-letter country code, or None if the code is invalid.
    """
    try:
        country = pycountry.countries.get(alpha_3=three_letter_code)
        if country:
            return country.alpha_2
        else:
            return None
    except LookupError:
        return None


def prepare_results_for_frontend(
    results: Dict[str, float]
) -> Dict[str, Union[List[float], float]]:
    """
    Given a dictionary of results, prepares the data for the frontend.

    Args:
        results (Dict[str, float]): A dictionary of results.

    Returns:
        Dict[str, Union[List[float], float]]: A dictionary containing the data, min, max, and average values.
    """
    result_values = list(results.values()) or [0]
    # if result is empty, set min and max to 0
    return {
        "data": results,
        "min": min(result_values),
        "max": max(result_values),
        "average": compute_average(list(results.values())),
    }


def convert_to_timestamp(date_str: str, delta_days: int = 0) -> int:
    """
    Converts a date string to a Unix timestamp.

    Args:
        date_str (str): A date string in the format of "YYYY-MM-DD".
        delta_days (int): An optional number of days to add to the date.

    Returns:
        int: The Unix timestamp of the date string.
    """
    dt_object = datetime.strptime(date_str, "%Y-%m-%d")
    dt_object += timedelta(days=delta_days)
    return int(dt_object.timestamp())


def compute_country_code_by_probe_id_dict(
    probes: List[Dict[str, Union[int, str]]]
) -> Dict[int, Optional[str]]:
    """
    Computes a dictionary of probe IDs and their corresponding country codes.

    Returns:
        Dict[int, Optional[str]]: A dictionary of probe IDs and their corresponding country codes.
    """
    return {
        probe["id"]: probe["country_code"]
        for probe in probes
        if probe["country_code"] is not None
    }


def get_dns_ripe_atlas_measurement_for_date(date: str) -> dict:
    """
    Given a date in string format, returns the results of a DNS measurement done by RIPE Atlas on that date.

    Args:
    date (str): The date in the format "YYYY-MM-DD".

    Returns:
    dict: The results of the DNS measurement in API format.
    """
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

    return response_results


def select_relevant_attributes_from_ripe_atlas_response(
    dns_api_result_per_probe: Dict[str, any],
) -> Dict[str, any]:
    """
    Given a dictionary of DNS API result per probe, returns a dictionary containing only the relevant attributes.
    in case if there is no result ( error during request), set default NO_RTT_RESULT = -1 value
    Args:
        dns_api_result_per_probe (Dict[str, any]): A dictionary of DNS API result per probe.

    Returns:
        Dict[str, any]: A dictionary containing only the relevant attributes.
    """
    return {
        "probe_id": dns_api_result_per_probe["prb_id"],
        "rtt_results": dns_api_result_per_probe.get("result", {}).get(
            "rt", NO_RTT_RESULT
        ),
    }


def compute_average_rtt_and_country_code(
    country_code_by_probe_id_hash: Dict[int, str],
    probe_id: int,
    rtt_results_of_probe: List[Dict[str, Union[int, float]]],
) -> Dict[str, Union[float, str]]:
    """
    Given a dictionary of country codes by probe ID, a probe ID, and a list of RTT results for that probe,
    computes the average RTT and the 3-letter country code for that probe.

    Args:
    country_code_by_probe_id_hash (Dict[int, str]): A dictionary of country codes by probe ID.
    probe_id (int): The ID of the probe.
    rtt_results_of_probe (List[Dict[str, Union[int, float]]]): A list of RTT results for the probe.

    Returns:
    Dict[str, Union[float, str]]: A dictionary containing the average RTT and the 3-letter country code for the probe.
    """
    # Compute the average RTT for the probe, ignoring any results that are equal to NO_RTT_RESULT
    average_rtt = compute_average(
        [
            result["rtt_results"]
            for result in rtt_results_of_probe
            if result["rtt_results"] != NO_RTT_RESULT
        ]
    )

    # Get the 3-letter country code for the probe
    country_code = convert_two_letter_to_three_letter_code(
        country_code_by_probe_id_hash.get(probe_id)
    )

    # Return a dictionary containing the average RTT and the 3-letter country code for the probe
    return {"rtt_result": average_rtt, "country_code": country_code}


def check_dns_measurements(date: str) -> Dict[str, Union[List[float], float]]:
    """
    Given a date in string format, retrieves the results of a DNS measurement done by RIPE Atlas on that date,
    computes the average RTT and the 3-letter country code for each probe, and returns the average RTT for each country.

    Args:
        date (str): The date in the format "YYYY-MM-DD".

    Returns:
        Dict[str, Union[List[float], float]]: A dictionary containing the average RTT for each country.
    """
    country_code_by_probe_id_hash: Dict[
        int, Optional[str]
    ] = compute_country_code_by_probe_id_dict(probes=probes_data)

    response_results: dict = get_dns_ripe_atlas_measurement_for_date(date)

    results: Dict[str, Union[List[float], float]] = (
        _.chain(response_results)
        .map(
            lambda api_result: select_relevant_attributes_from_ripe_atlas_response(
                dns_api_result_per_probe=api_result
            )
        )
        # select only relevant fields from response
        .group_by("probe_id")
        # group all the result by probe id
        .map(
            lambda values, key: compute_average_rtt_and_country_code(
                country_code_by_probe_id_hash,
                probe_id=key,
                rtt_results_of_probe=values,
            )
        )
        # we compute average rtt for each probe and its 3-letter country code
        # and remove its connection to the probe id
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


def compute_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Given two dates in string format, returns a list of all dates in the range.

    Args:
    start_date (str): The start date in the format "YYYY-MM-DD".
    end_date (str): The end date in the format "YYYY-MM-DD".

    Returns:
    List[str]: A list of all dates in the range in the format "YYYY-MM-DD".
    """
    # Convert the input date strings into datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate the difference between the two dates
    delta = end_date - start_date

    # Generate a list of all dates in the range
    dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

    # Convert datetime objects back into strings
    return [date.strftime("%Y-%m-%d") for date in dates]


def compute_dns_between_dates(
    start_date: str, end_date: str
) -> List[Dict[str, Union[str, int]]]:
    """
    Given two dates in string format, returns a list of dictionaries containing DNS measurements for each date in the range.

    Args:
    start_date (str): The start date in the format "YYYY-MM-DD".
    end_date (str): The end date in the format "YYYY-MM-DD".

    Returns:
    List[Dict[str, Union[str, int]]]: A list of dictionaries containing DNS measurements for each date in the range.
    """
    return [
        {"name": date, **check_dns_measurements(date)}
        for date in compute_date_range(start_date, end_date)
    ]


# IPv6 functions


def check_probes_asn_version_support(
    probe_ids: List[int], start_date: str, end_date: str
) -> List[Dict[str, Union[str, int]]]:
    """
    Given a list of probe ids, start date and end date, returns a list of dictionaries containing the ASN and date for each probe.

    Args:
    probe_ids (List[int]): A list of probe ids.
    start_date (str): The start date in the format "YYYY-MM-DD".
    end_date (str): The end date in the format "YYYY-MM-DD".

    Returns:
    List[Dict[str, Union[str, int]]]: A list of dictionaries containing the ASN and date for each probe.
    """
    url_path = "/api/v2/probes/archive"
    change_timestamp_format = lambda date: datetime.strptime(
        date, "%Y%m%d"
    ).strftime("%Y-%m-%d")
    result = []
    for probe_ids_sublist in _.chunk(probe_ids, 500):
        # split the list of probe ids into sublists of 500 probe ids
        # if we don't do this the request will fail because the url will be too long
        filters = {
            "probe": probe_ids_sublist,
            "date__gte": start_date,
            "date__lte": end_date,
        }
        is_success, response = AtlasRequest(**{"url_path": url_path}).get(
            **filters
        )
        if is_success:
            result.extend(
                [
                    {
                        "asn_v6": result["asn_v6"],
                        "asn_v4": result["asn_v4"],
                        "date": change_timestamp_format(result["date"]),
                    }
                    for result in response["results"]
                    if (
                        result["asn_v6"] is not None
                        or result["asn_v4"] is not None
                    )
                ]
            )

    return result


def compute_distinct_asn_ids_per_type(
    probes_asn_status_by_date: List[Dict[str, Union[str, int]]]
) -> Dict[str, List[str]]:
    """
    Given a list of dictionaries containing the ASN and date for each probe, returns a dictionary containing the distinct ASN names for IPv4 and IPv6.

    Args:
    probes_asn_status_by_date (List[Dict[str, Union[str, int]]]): A list of dictionaries containing the ASN and date for each probe.

    Returns:
    Dict[str, List[str]]: A dictionary containing the distinct ASN names for IPv4 and IPv6.
    """
    return {
        "distinct_asn_v4_names": _.chain(probes_asn_status_by_date)
        .group_by("asn_v4")
        .keys()
        .value(),
        "distinct_asn_v6_names": _.chain(probes_asn_status_by_date)
        .group_by("asn_v6")
        .keys()
        .value(),
    }


def compute_amount_of_asns(
    grouped_asn_dict: Dict[str, List[str]]
) -> Dict[str, int]:
    """
    Computes the amount of distinct ASN IDs for IPv4 and IPv6 from a dictionary of grouped ASN IDs.

    Args:
        grouped_asn_dict: A dictionary containing the distinct ASN IDs for IPv4 and IPv6.

    Returns:
        A dictionary containing the amount of distinct ASN IDs for IPv4 and IPv6, as well as the total amount of ASN IDs.
    """
    return {
        "asn_amount": len(
            _.union(
                grouped_asn_dict["distinct_asn_v4_names"],
                grouped_asn_dict["distinct_asn_v6_names"],
            )
        ),
        "asn_v4_amount": len(grouped_asn_dict["distinct_asn_v4_names"]),
        "asn_v6_amount": len(grouped_asn_dict["distinct_asn_v6_names"]),
    }


def compute_percentage_per_date(
    msn_amounts: Dict[str, int], date: str
) -> Dict[str, Union[str, float]]:
    """
    Computes the percentage of IPv6 addresses for a given date.

    Args:
        msn_amounts (Dict[str, int]): A dictionary containing the amount of distinct ASN IDs for IPv4 and IPv6, as well as the total amount of ASN IDs.
        date (str): The date for which to compute the percentage.

    Returns:
        Dict[str, Union[str, float]]: A dictionary containing the name of the date and the percentage of IPv6 addresses.
    """
    percentage = (
        ((msn_amounts["asn_v6_amount"] / msn_amounts["asn_amount"]) * 100)
        if msn_amounts["asn_amount"] != 0
        and msn_amounts["asn_v6_amount"] is not None
        else 0
    )
    return {"name": date, "ip_v6": f"{percentage:.2f}"}


def compute_ipv6_percentage(
    country_code: str, start_date: str, finish_date: str
) -> List[Dict[str, Union[str, float]]]:
    """
    Computes the percentage of IPv6 addresses for a given country and date range.

    Args:
        country_code (str): The country code for which to compute the percentage.
        start_date (str): The start date of the date range.
        finish_date (str): The end date of the date range.

    Returns:
        List[Dict[str, Union[str, float]]]: A list of dictionaries containing the name of the date and the percentage of IPv6 addresses.
    """
    probe_ids_by_country = [
        probe["id"]
        for probe in probes_data
        if probe["country_code"] == country_code
    ]
    probes_status = check_probes_asn_version_support(
        probe_ids_by_country,
        start_date,
        finish_date,
    )
    result = (
        _.chain(probes_status).group_by("date")
        # group all the result by date
        .map_values(
            lambda probes_status_by_day, date: compute_distinct_asn_ids_per_type(
                probes_asn_status_by_date=probes_status_by_day
            )
        )
        # for each date, compute the distinct asn ids for ipv4 and ipv6
        # as a result per date we have a dictionary with the distinct asn ids for ipv4 and ipv6
        # format of data :{"distinct_asn_v4_names": [...], "distinct_asn_v6_names": [...]}
        .map_values(
            lambda grouped_asn_per_type, date: compute_amount_of_asns(
                grouped_asn_dict=grouped_asn_per_type
            )
        )
        # for each date, compute the amount of distinct asn ids for ipv4 and ipv6 and their union (total amount)
        # as a result per date we have a dictionary with format
        # {"asn_amount": m+n - intersection, "asn_v4_amount": m  "asn_v6_amount": n}
        .map(
            lambda asn_amounts_per_date, date: compute_percentage_per_date(
                msn_amounts=asn_amounts_per_date, date=date
            )
        )
        # for each date, compute the percentage of probes that support ipv6
        # as a result per date we have a dictionary with format {"name": date, "ipv6": percentage}
        .value()
    )
    return result


def compute_fragmented_data(
    start_date: str,
    end_date: str,
    countries_data: List[Dict[str, Union[str, float]]],
    computation_routine: callable = compute_dns_between_dates,
) -> List[Dict[str, Union[str, float]]]:
    """
    Computes the fragmented data between two dates for a given list of countries.

    Args:
    - start_date (str): The start date in the format of 'YYYY-MM-DD'.
    - end_date (str): The end date in the format of 'YYYY-MM-DD'.
    - countries_data (list): A list of dictionaries containing the some measurements for each country in format countries_data = [{'name': '2020-01-01',"US": 25.1,.. },...]
    - computation_routine (callable): A function that computes the DNS measurements between two dates.

    Returns:
    - list: A list of dictionaries containing the DNS/IPv6 measurements for each country between the start and end dates.
    """
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

    # Check if the start date is within the cached dates
    if (
        start_date_timestamp >= first_date_in_cache_timestamp
        and start_date_timestamp <= last_day_in_cache_timestamp
    ):
        start_index = cached_dates.index(start_date)
        if end_date_timestamp <= last_day_in_cache_timestamp:
            end_index = cached_dates.index(end_date)
            return countries_data[start_index : end_index + 1]
        else:
            # end_date > last_day_in_cache_timestamp
            result = countries_data[start_index:]
            result.extend(computation_routine(last_day_in_cache, end_date)[1:])
            return result

    # Check if the start date is before the cached dates and the end date is within the cached dates
    elif (
        start_date_timestamp < first_date_in_cache_timestamp
        and end_date_timestamp >= first_date_in_cache_timestamp
        # and end_date_timestamp <= last_day_in_cache_timestamp
    ):
        # start_date < first_date_in_cache_timestamp
        if end_date_timestamp <= last_day_in_cache_timestamp:
            end_index = cached_dates.index(end_date)
            result = computation_routine(start_date, first_date_in_cache)
            result.extend(countries_data[1 : end_index + 1])
            return result
        else:
            # end_date > last_day_in_cache_timestamp
            result = computation_routine(start_date, first_date_in_cache)
            result.extend(countries_data[1:-1])
            result.extend(computation_routine(last_day_in_cache, end_date))
            return result

    # If the start and end dates are not within the cached dates
    else:
        return computation_routine(start_date, end_date)
