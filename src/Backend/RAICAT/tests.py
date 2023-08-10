from datetime import datetime
from typing import Dict, List, Union
from unittest.mock import patch, MagicMock
import unittest

import pycountry
from ripe.atlas.sagan import Result
import pytest

from .utils import (
    STOPPED,
    NO_RTT_RESULT,
    compute_average,
    prepare_results_for_frontend,
    convert_to_timestamp,
    compute_country_code_by_probe_id_dict,
    get_dns_ripe_atlas_measurement_for_date,
    convert_two_letter_to_three_letter_code,
)


class TestUtils(unittest.TestCase):
    def test_compute_average(self):
        self.assertEqual(compute_average([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(compute_average([1, 1, 1, 1, 1]), 1.0)
        self.assertEqual(compute_average([]), 0)

    def test_prepare_results_for_frontend(self):
        results = {"a": 1.0, "b": 2.0, "c": 3.0}
        expected_output = {
            "data": results,
            "min": 0,
            "max": 3.0,
            "average": 2.0,
        }
        self.assertEqual(
            prepare_results_for_frontend(results), expected_output
        )

    def test_convert_to_timestamp(self):
        self.assertEqual(convert_to_timestamp("2022-01-01"), 1640995200)
        self.assertEqual(
            convert_to_timestamp("2022-01-01", delta_days=1), 1641081600
        )

    # def test_compute_country_code_by_probe_id_dict(self):
    #     expected_output = {
    #         1: "US",
    #         2: "CA",
    #         3: "MX",
    #     }
    #     with patch(
    #         "RAICAT.utils.probes_data",
    #         [
    #             {"id": 1, "country_code": "US"},
    #             {"id": 2, "country_code": "CA"},
    #             {"id": 3, "country_code": "MX"},
    #             {"id": 4, "country_code": None},
    #         ],
    #     ):
    #         self.assertEqual(compute_country_code_by_probe_id_dict(), expected_output)

    # def test_get_dns_ripe_atlas_measurement_for_date(self):
    #     expected_output = {"results": []}
    #     with patch("ripe.atlas.cousteau.AtlasRequest") as mock_request:
    #         mock_request().get.return_value = expected_output
    #         self.assertEqual(
    #             get_dns_ripe_atlas_measurement_for_date("2022-01-01"), expected_output
    #         )

    # def test_convert_two_letter_to_three_letter_code(self):
    #     self.assertEqual(convert_two_letter_to_three_letter_code("US"), "USA")
    #     self.assertIsNone(convert_two_letter_to_three_letter_code("XX"))
