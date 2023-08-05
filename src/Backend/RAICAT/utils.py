from datetime import datetime, timedelta
from typing import List, Dict, Union
from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.sagan import Result, DnsResult
import pydash as _
import pycountry
from ipwhois import IPWhois
import concurrent.futures
from .probes_db import probes_data


STOPPED: int = 4


def get_measurement_results(measurement_id: int) -> Union[Dict, None]:
    """
    Given a measurement ID, returns the results of the measurement.

    Args:
        measurement_id (int): The ID of the measurement.

    Returns:
        Union[Dict, None]: A dictionary containing the results of the measurement, or None if the request failed.
    """
    url_path = f"/api/v2/measurements/{measurement_id}/results/"
    is_success, response_results = AtlasRequest(**{"url_path": url_path}).get()
    if is_success:
        return response_results
    else:
        return None


def get_probes_geolocation_list_by_id(probe_id_list: List[str]) -> List[Dict]:
    """
    Given a list of probe IDs, returns a list of dictionaries containing the geolocation information for each probe.

    Args:
        probe_id_list (List[str]): A list of probe IDs.

    Returns:
        List[Dict]: A list of dictionaries containing the geolocation information for each probe.
    """
    url_path = "/api/v2/probes/"
    result = []
    for sub_list in [
        probe_id_list[i : i + 100] for i in range(0, len(probe_id_list), 100)
    ]:
        is_success, response_results = AtlasRequest(
            **{"url_path": url_path}
        ).get(**{"id__in": ",".join(sub_list)})
        if is_success:
            result.extend(response_results["results"])
        else:
            continue
    return result


def map_measurement_result_to_probe_info(parsed_result: Result) -> Dict:
    """
    Given a parsed measurement result, returns a dictionary containing the probe ID and RTT results.

    Args:
        parsed_result (Result): A parsed measurement result.

    Returns:
        Dict: A dictionary containing the probe ID and RTT results.
    """
    return {
        "probe_id": parsed_result.probe_id,
        "rtt_results": [parsed_result.responses[0].response_time],
    }


def create_measurement_hash(measurement_id: int) -> List[Dict]:
    """
    Given a measurement ID, returns a list of dictionaries containing the probe ID, RTT results, and geolocation information for each probe.

    Args:
        measurement_id (int): The ID of the measurement.

    Returns:
        List[Dict]: A list of dictionaries containing the probe ID, RTT results, and geolocation information for each probe.
    """

    def find_object_by_id(collection, id):
        for obj in collection:
            if obj["id"] == id:
                return obj  # Return the object if found

    meausrement_results = get_measurement_results(measurement_id)
    probes_information = [
        map_measurement_result_to_probe_info(DnsResult(result))
        for result in meausrement_results
        if not DnsResult(result).is_error
    ]
    probes_geolocation = get_probes_geolocation_list_by_id(
        [str(probe_obj["probe_id"]) for probe_obj in probes_information]
    )
    for probe_info in probes_information:
        according_probe_geolocation = find_object_by_id(
            probes_geolocation, probe_info["probe_id"]
        )
        probe_info["geolocation"] = according_probe_geolocation
    return probes_information


def merge_measurement_results(
    measurement_hash: List[Dict], previous_results: List[Dict]
) -> List[Dict]:
    """
    Given a list of dictionaries containing the probe ID, RTT results, and geolocation information for each probe, and a list of previous results, returns a merged list of dictionaries containing the probe ID, RTT results, and geolocation information for each probe.

    Args:
        measurement_hash (List[Dict]): A list of dictionaries containing the probe ID, RTT results, and geolocation information for each probe.
        previous_results (List[Dict]): A list of previous results.

    Returns:
        List[Dict]: A merged list of dictionaries containing the probe ID, RTT results, and geolocation information for each probe.
    """
    if previous_results == []:
        return measurement_hash
    else:
        for probe_info in measurement_hash:
            for previous_probe_info in previous_results:
                if probe_info["probe_id"] == previous_probe_info["probe_id"]:
                    previous_probe_info["rtt_results"].extend(
                        probe_info["rtt_results"]
                    )
                    break
            else:
                previous_results.append(probe_info)
        return previous_results


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


def get_measurements_collection_by_date_and_type(
    date: str, measurement_type: str
) -> Union[List[Dict], None]:
    """
    Given a date and measurement type, returns a list of dictionaries containing information about the measurements.

    Args:
        date (str): The date in the format "YYYY-MM-DD".
        measurement_type (str): The type of measurement.

    Returns:
        Union[List[Dict], None]: A list of dictionaries containing information about the measurements, or None if the request failed.
    """
    timestamp = datetime.strptime(date, "%Y-%m-%d").timestamp()
    filters = {
        "type": measurement_type,
        "status": STOPPED,
        "start_time__gte": timestamp,
        "start_time__lt": timestamp + 24 * 60 * 60,
        "fields": "id,start_time,stop_time,af,query_argument,query_type,result",
    }
    url_path = "/api/v2/measurements/"
    is_success, response = AtlasRequest(**{"url_path": url_path}).get(
        **filters
    )
    if is_success:
        return response["results"]
    else:
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


def check_dns_measurements(date):
    measurements = get_measurements_collection_by_date_and_type(date, "dns")
    results = []
    for measurement in measurements:
        measurement_hash = create_measurement_hash(measurement.get("id"))
        results = merge_measurement_results(measurement_hash, results)
    grouped_result = compute_average_by_country(results)
    return prepare_results_for_frontend(grouped_result)


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
    if percentage!=0:
        data.append({"name": day, "ipv6": percentage})
    return data


def check_as_for_probes(country_code, start_date, finish_date):
    #probes = get_probes_for_country(country_code)
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(finish_date, "%Y-%m-%d")
    delta = end_datetime - start_datetime
    #ids = [item["id"] for item in probes]
    ids = [item["id"] for item in probes_data if item["country_code"] == country_code]
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
        data = add_results_ipv6(data, current_day, f"{percentage:.2f}")
    return data
