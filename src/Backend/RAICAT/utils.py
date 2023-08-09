from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional
from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.sagan import Result, DnsResult
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
    return {
        "data": results,
        "min": min(list(results.values()) + [0]),
        "max": max(list(results.values()) + [0]),
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


def compute_country_code_by_probe_id_dict() -> Dict[int, Optional[str]]:
    """
    Computes a dictionary of probe IDs and their corresponding country codes.

    Returns:
        Dict[int, Optional[str]]: A dictionary of probe IDs and their corresponding country codes.
    """
    return {
        probe["id"]: probe["country_code"]
        for probe in probes_data
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


def check_dns_measurements(date: str) -> Dict[str, Union[List[float], float]]:
    """
    Given a date in string format, retrieves the results of a DNS measurement done by RIPE Atlas on that date,
    computes the average RTT and the 3-letter country code for each probe, and returns the average RTT for each country.

    Args:
        date (str): The date in the format "YYYY-MM-DD".

    Returns:
        Dict[str, Union[List[float], float]]: A dictionary containing the average RTT for each country.
    """
def check_dns_measurements(
    date: str,
) -> Dict[str, Union[List[float], float]]:
    country_code_by_probe_id_hash: Dict[
        int, Optional[str]
    ] = compute_country_code_by_probe_id_dict()

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
    return data


def check_as_for_probes(country_code, start_date, finish_date):

    ids = [
        item["id"]
        for item in probes_data
        if item["country_code"] == country_code
    ]
    results = probes_ipv6_check(
        ids,
        start_date,
        finish_date,
    )
    data = []

    for date in compute_date_range(start_date, finish_date):
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
        data = add_results_ipv6(data, current_day, f"{percentage:.2f}")
    return data
