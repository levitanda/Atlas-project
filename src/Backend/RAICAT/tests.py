from datetime import datetime
from typing import Dict, List, Union
from unittest import mock
import unittest


from .utils import (
    STOPPED,
    NO_RTT_RESULT,
    compute_average,
    prepare_results_for_frontend,
    convert_to_timestamp,
    compute_country_code_by_probe_id_dict,
    get_dns_ripe_atlas_measurement_for_date,
    convert_two_letter_to_three_letter_code,
    select_relevant_attributes_from_ripe_atlas_response,
    compute_average_rtt_and_country_code,
    check_dns_measurements,
    compute_date_range,
    compute_dns_between_dates,
    check_probes_asn_version_support,
    compute_distinct_asn_ids_per_type,
    compute_amount_of_asns,
    compute_percentage_per_date,
    compute_ipv6_percentage,
    compute_fragmented_data,
)
from .fixtures.dns_ripe_atlas_fixtures import (
    dns_ripe_atlas_measurements_per_2021_01_01_api_response_fixture,
)
from .fixtures.computed_dns_result import (
    pre_computed_dns_result_2021_01_01_fixture,
    computed_dns_result_between_2021_01_01_and_2021_01_02_fixture,
)


class TestUtils(unittest.TestCase):
    def test_compute_average(self):
        # Test that the function returns the correct average for a list of integers
        self.assertEqual(compute_average([1, 2, 3, 4, 5]), 3.0)
        # Test that the function returns the correct average for a list of identical integers
        self.assertEqual(compute_average([1, 1, 1, 1, 1]), 1.0)
        # Test that the function returns 0 for an empty list
        self.assertEqual(compute_average([]), 0)

    def test_convert_two_letter_to_three_letter_code(self):
        # Test valid input
        self.assertEqual(convert_two_letter_to_three_letter_code("US"), "USA")
        self.assertEqual(convert_two_letter_to_three_letter_code("GB"), "GBR")
        self.assertEqual(convert_two_letter_to_three_letter_code("CA"), "CAN")

        # Test invalid input
        self.assertIsNone(convert_two_letter_to_three_letter_code("XX"))
        self.assertIsNone(convert_two_letter_to_three_letter_code("123"))
        self.assertIsNone(convert_two_letter_to_three_letter_code(""))

    def test_prepare_results_for_frontend(self):
        # Define a dictionary of results
        input_results = {"a": 1.0, "b": 2.0, "c": 3.0}
        # Define the expected output dictionary
        expected_output = {
            "data": input_results,
            "min": 1.0,
            "max": 3.0,
            "average": 2.0,
        }
        # Test that the prepare_results_for_frontend function returns the expected output
        self.assertEqual(
            prepare_results_for_frontend(input_results), expected_output
        )

    def test_convert_to_timestamp(self):
        # Test that the function returns the correct timestamp for a given date
        self.assertEqual(convert_to_timestamp("2022-01-01"), 1640995200)
        # Test that the function returns the correct timestamp for a given date and delta_days
        self.assertEqual(
            convert_to_timestamp("2022-01-01", delta_days=1), 1641081600
        )

    def test_compute_country_code_by_probe_id_dict(self):
        # Define a list of probes with their IDs and country codes
        probes = [
            {"id": 1, "country_code": "US"},
            {"id": 2, "country_code": "CA"},
            {"id": 3, "country_code": None},
            {"id": 4, "country_code": "MX"},
        ]
        # Define the expected result of the function
        expected_result = {1: "US", 2: "CA", 4: "MX"}
        # Call the function with the probes list and check if the result matches the expected result
        result = compute_country_code_by_probe_id_dict(probes)
        self.assertEqual(result, expected_result)

    def test_get_dns_ripe_atlas_measurement_for_date(self):
        # Define the expected output of the function
        expected_output = (
            dns_ripe_atlas_measurements_per_2021_01_01_api_response_fixture
        )
        # Call the function with a specific date and check if the result matches the expected output
        real_result = get_dns_ripe_atlas_measurement_for_date("2021-01-01")
        self.assertEqual(real_result, expected_output)

    def test_select_relevant_attributes_from_ripe_atlas_response(self):
        # Test case 1: valid input
        input_dict = {"prb_id": 123, "result": {"rt": 10.0}}
        expected_output_dict = {"probe_id": 123, "rtt_results": 10.0}
        self.assertEqual(
            select_relevant_attributes_from_ripe_atlas_response(input_dict),
            expected_output_dict,
        )

        # Test case 2: missing "result" key
        input_dict = {"prb_id": 123}
        expected_output_dict = {"probe_id": 123, "rtt_results": -1}
        self.assertEqual(
            select_relevant_attributes_from_ripe_atlas_response(input_dict),
            expected_output_dict,
        )

        # Test case 3: missing "rt" key in "result" dict
        input_dict = {"prb_id": 123, "result": {}}
        expected_output_dict = {"probe_id": 123, "rtt_results": -1}
        self.assertEqual(
            select_relevant_attributes_from_ripe_atlas_response(input_dict),
            expected_output_dict,
        )

    def test_compute_average_rtt_and_country_code(self):
        # Define test data
        country_code_by_probe_id_hash = {1: "US", 2: "FR", 3: "JP"}
        probe_id = 2
        rtt_results_of_probe = [
            {"rtt_results": 10.0},
            {"rtt_results": 20.0},
            {"rtt_results": NO_RTT_RESULT},
            {"rtt_results": 30.0},
        ]

        # Mock the `compute_average` and `convert_two_letter_to_three_letter_code` functions
        with mock.patch(
            "RAICAT.utils.compute_average"
        ) as mock_compute_average, mock.patch(
            "RAICAT.utils.convert_two_letter_to_three_letter_code"
        ) as mock_convert_two_letter_to_three_letter_code:
            # Configure the mock `compute_average` function to return a fixed value
            mock_compute_average.return_value = 20.0

            # Configure the mock `convert_two_letter_to_three_letter_code` function to return a fixed value
            mock_convert_two_letter_to_three_letter_code.return_value = "FRA"

            # Call the function under test
            result = compute_average_rtt_and_country_code(
                country_code_by_probe_id_hash, probe_id, rtt_results_of_probe
            )

            # Assert the expected output
            self.assertEqual(
                result, {"rtt_result": 20.0, "country_code": "FRA"}
            )

            # Assert that the `compute_average` function was called with the expected arguments
            mock_compute_average.assert_called_once_with([10.0, 20.0, 30.0])

            # Assert that the `convert_two_letter_to_three_letter_code` function was called with the expected arguments
            mock_convert_two_letter_to_three_letter_code.assert_called_once_with(
                "FR"
            )

    # @mock.patch("RAICAT.utils.compute_country_code_by_probe_id_dict")
    @mock.patch("RAICAT.utils.get_dns_ripe_atlas_measurement_for_date")
    def test_check_dns_measurements(
        self,
        mock_get_dns,
    ):
        # Set up mock data
        mock_get_dns.return_value = (
            dns_ripe_atlas_measurements_per_2021_01_01_api_response_fixture
        )

        # Call the function with mock data
        result = check_dns_measurements("2021-01-01")

        # Check that the result is as expected
        self.assertEqual(result, pre_computed_dns_result_2021_01_01_fixture)

    def test_compute_date_range(self):
        # Define the start and end dates for the date range
        start_date = "2022-01-01"
        end_date = "2022-01-03"
        # Define the expected result of the function
        expected_result = ["2022-01-01", "2022-01-02", "2022-01-03"]
        # Call the compute_date_range function with the start and end dates
        result = compute_date_range(start_date, end_date)
        # Check that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_compute_dns_between_dates(self):
        # Define the expected result of the function
        expected_result = (
            computed_dns_result_between_2021_01_01_and_2021_01_02_fixture
        )

        # Call the compute_ipv6_percentage function with the input data
        result = compute_dns_between_dates("2021-01-01", "2021-01-02")
        # Check that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_check_probes_asn_version_support(self):
        # Define the input parameters for the function
        probe_ids = [1, 2, 3]
        start_date = "2022-01-01"
        end_date = "2022-01-03"
        # Call the check_probes_asn_version_support function with the input parameters
        result = check_probes_asn_version_support(
            probe_ids, start_date, end_date
        )
        # Check that the result is a list
        self.assertIsInstance(result, list)
        # Check that each item in the list is a dictionary
        for item in result:
            self.assertIsInstance(item, dict)
            # Check that each dictionary contains the ASN version for IPv4 and IPv6, as well as the date
            self.assertIn("asn_v4", item)
            self.assertIn("asn_v6", item)
            self.assertIn("date", item)
            # Check that the ASN versions are integers
            self.assertIsInstance(item["asn_v4"], int)
            self.assertIsInstance(item["asn_v6"], int)
            # Check that the date is a string in the format "YYYY-MM-DD"
            self.assertIsInstance(item["date"], str)
            self.assertEqual(
                datetime.strptime(item["date"], "%Y-%m-%d").strftime(
                    "%Y-%m-%d"
                ),
                item["date"],
            )

    def test_compute_distinct_asn_ids_per_type(self):
        # Define a list of dictionaries representing the ASN status of probes by date
        probes_asn_status_by_date = [
            {"asn_v4": "AS1", "asn_v6": "AS2"},
            {"asn_v4": "AS1", "asn_v6": "AS1"},
            {"asn_v4": "AS4", "asn_v6": "AS3"},
            {"asn_v4": "AS5", "asn_v6": "AS6"},
            {"asn_v4": "AS5", "asn_v6": "AS6"},
        ]
        # Define the expected result of the function
        expected_result = {
            "distinct_asn_v4_names": ["AS1", "AS4", "AS5"],
            "distinct_asn_v6_names": ["AS2", "AS1", "AS3", "AS6"],
        }
        # Call the compute_distinct_asn_ids_per_type function with the input data
        result = compute_distinct_asn_ids_per_type(probes_asn_status_by_date)
        # Check that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_compute_amount_of_asns(self):
        # Define a dictionary of distinct ASN names for IPv4 and IPv6
        grouped_asn_dict = {
            "distinct_asn_v4_names": ["ASN1", "ASN2", "ASN3"],
            "distinct_asn_v6_names": ["ASN1", "ASN4", "ASN5"],
        }
        # Define the expected result of the function
        expected_result = {
            "asn_amount": 5,
            "asn_v4_amount": 3,
            "asn_v6_amount": 3,
        }
        # Call the compute_amount_of_asns function with the input data
        result = compute_amount_of_asns(grouped_asn_dict)
        # Check that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_compute_percentage_per_date(self):
        # Test case 1: msn_amounts contains 0 ASN IDs
        msn_amounts = {"asn_amount": 0, "asn_v4_amount": 0, "asn_v6_amount": 0}
        result = compute_percentage_per_date(msn_amounts, "2022-01-01")
        self.assertEqual(result, {"name": "2022-01-01", "ip_v6": "0.00"})

        # Test case 2: msn_amounts contains only IPv4 ASN IDs
        msn_amounts = {"asn_amount": 2, "asn_v4_amount": 2, "asn_v6_amount": 0}
        result = compute_percentage_per_date(msn_amounts, "2022-01-01")
        self.assertEqual(result, {"name": "2022-01-01", "ip_v6": "0.00"})

        # Test case 3: msn_amounts contains only IPv6 ASN IDs
        msn_amounts = {"asn_amount": 2, "asn_v4_amount": 0, "asn_v6_amount": 2}
        result = compute_percentage_per_date(msn_amounts, "2022-01-01")
        self.assertEqual(result, {"name": "2022-01-01", "ip_v6": "100.00"})

        # Test case 4: msn_amounts contains both IPv4 and IPv6 ASN IDs
        msn_amounts = {"asn_amount": 4, "asn_v4_amount": 2, "asn_v6_amount": 2}
        result = compute_percentage_per_date(msn_amounts, "2022-01-01")
        self.assertEqual(result, {"name": "2022-01-01", "ip_v6": "50.00"})

    def test_compute_fragmented_data(self):
        # Define test data
        def computation_routine(start_date, end_date):
            return [
                {"name": item, "US": 25.1, "UK": 30.2}
                for item in compute_date_range(start_date, end_date)
            ]

        start_date = "2022-01-01"
        end_date = "2022-01-03"

        countries_data = [
            {"name": "2022-01-01", "US": 25.1, "UK": 30.2},
            {"name": "2022-01-02", "US": 28.5, "UK": 31.7},
            {"name": "2022-01-03", "US": 27.3, "UK": 29.8},
        ]

        # Call the function being tested
        result = compute_fragmented_data(
            start_date,
            end_date,
            countries_data,
            computation_routine,
        )
        self.assertEqual(result, countries_data)
        # ----------------------------
        start_date = "2022-01-01"
        end_date = "2022-01-04"

        countries_data = [
            {"name": "2022-01-01", "US": 25.1, "UK": 30.2},
            {"name": "2022-01-02", "US": 28.5, "UK": 31.7},
            {"name": "2022-01-03", "US": 27.3, "UK": 29.8},
        ]

        # Call the function being tested
        result = compute_fragmented_data(
            start_date,
            end_date,
            countries_data,
            computation_routine,
        )
        expected_output = countries_data + [
            {"name": "2022-01-04", "US": 25.1, "UK": 30.2}
        ]
        self.assertEqual(result, expected_output)

        # ----------------------------
        start_date = "2021-12-31"
        end_date = "2022-01-03"

        countries_data = [
            {"name": "2022-01-01", "US": 25.1, "UK": 30.2},
            {"name": "2022-01-02", "US": 28.5, "UK": 31.7},
            {"name": "2022-01-03", "US": 27.3, "UK": 29.8},
        ]
        result = compute_fragmented_data(
            start_date,
            end_date,
            countries_data,
            computation_routine,
        )
        expected_output = [
            {"name": "2021-12-31", "US": 25.1, "UK": 30.2}
        ] + countries_data
        self.assertEqual(result, expected_output)
        # ----------------------------
        start_date = "2021-12-31"
        end_date = "2022-01-04"

        countries_data = [
            {"name": "2022-01-01", "US": 25.1, "UK": 30.2},
            {"name": "2022-01-02", "US": 25.1, "UK": 30.2},
            {"name": "2022-01-03", "US": 25.1, "UK": 30.2},
        ]
        result = compute_fragmented_data(
            start_date,
            end_date,
            countries_data,
            computation_routine,
        )
        expected_output = (
            [{"name": "2021-12-31", "US": 25.1, "UK": 30.2}]
            + countries_data
            + [{"name": "2022-01-04", "US": 25.1, "UK": 30.2}]
        )
        self.assertEqual(result, expected_output)
