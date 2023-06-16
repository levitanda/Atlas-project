from datetime import datetime
from ripe.atlas.cousteau import AtlasRequest, AtlasResultsRequest
from ripe.atlas.sagan import Result, DnsResult
import pydash as _
import pycountry
from ipwhois import IPWhois

STOPPED = 4


def get_measurements_collection_by_date_and_type(date, measurement_type):
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


def get_measurement_results(measurement_id):
    url_path = f"/api/v2/measurements/{measurement_id}/results/"
    is_success, response_results = AtlasRequest(**{"url_path": url_path}).get()
    if is_success:
        return response_results
    else:
        return None


def get_probes_geolocation_list_by_id(probe_id_list):
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


def map_measurement_result_to_probe_info(parsed_result):
    return {
        "probe_id": parsed_result.probe_id,
        "rtt_results": [parsed_result.responses[0].response_time],
    }


def create_measurement_hash(measurement_id):
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


def merge_measurement_results(measurement_hash, previous_results):
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


def compute_average_by_country(results):
    def compute_average(x):
        if len(x) == 0:
            return 0
        return sum(x) / len(x)

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


def check_dns_measurements(date):
    measurements = get_measurements_collection_by_date_and_type(date, "dns")
    results = []
    for measurement in measurements:
        # print('Measurement ID:', measurement.get("id"))
        # print('Start Time:', datetime.fromtimestamp(
        #     measurement.get("start_time")))
        # print('Stop Time:', datetime.fromtimestamp(
        #     measurement.get("stop_time")))
        # print(
        #     f"Query: {measurement.get('af')} {measurement.get('query_argument')} {measurement.get('query_type')}")
        # print('Results Link:', measurement.get("result"))
        # print('----')
        measurement_hash = create_measurement_hash(measurement.get("id"))
        results = merge_measurement_results(measurement_hash, results)
        grouped_result = compute_average_by_country(results)
    return grouped_result


def convert_two_letter_to_three_letter_code(two_letter_code):
    try:
        country = pycountry.countries.get(alpha_2=two_letter_code)
        if country:
            return country.alpha_3
        else:
            return None
    except LookupError:
        return None
