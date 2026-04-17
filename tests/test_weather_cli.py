import unittest
from unittest.mock import patch

import click
from click.testing import CliRunner

from weather import WeatherError, cli, get_current_weather, get_location_by_zipcode


class WeatherCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @patch("weather.get_location_by_zipcode")
    def test_where_is_with_zipcode(self, mock_get_location_by_zipcode):
        mock_get_location_by_zipcode.return_value = {
            "city": "New York",
            "state": "New York",
            "zipcode": "10001",
        }

        result = self.runner.invoke(cli, ["where-is", "--zipcode", "10001"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), "10001 is in New York, New York.")
        mock_get_location_by_zipcode.assert_called_once_with("10001")

    @patch("weather.get_current_location")
    def test_where_is_without_zipcode_when_location_missing(self, mock_get_current_location):
        mock_get_current_location.return_value = None

        result = self.runner.invoke(cli, ["where-is"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Unable to determine current location.", result.output)

    @patch("weather.get_location_by_zipcode")
    def test_where_is_with_invalid_zipcode_error(self, mock_get_location_by_zipcode):
        mock_get_location_by_zipcode.side_effect = click.ClickException(
            "Invalid zipcode. Please provide a 5-digit US zipcode."
        )

        result = self.runner.invoke(cli, ["where-is", "--zipcode", "ABC"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Invalid zipcode", result.output)

    @patch("weather.get_location_by_zipcode")
    @patch("weather.get_current_weather")
    def test_current_with_zipcode(self, mock_get_current_weather, mock_get_location_by_zipcode):
        mock_get_location_by_zipcode.return_value = {
            "city": "New York",
            "state": "New York",
            "zipcode": "10001",
        }
        mock_get_current_weather.return_value = {
            "temperature_f": "68",
            "condition": "Sunny",
        }

        result = self.runner.invoke(cli, ["current", "--zipcode", "10001"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output.strip(),
            "It is currently 68ºF, and Sunny in New York, New York.",
        )
        mock_get_location_by_zipcode.assert_called_once_with("10001")
        mock_get_current_weather.assert_called_once_with("10001")

    @patch("weather.get_current_location")
    @patch("weather.get_current_weather")
    def test_current_without_zipcode(self, mock_get_current_weather, mock_get_current_location):
        mock_get_current_location.return_value = {
            "city": "Austin",
            "state": "Texas",
            "zipcode": "78701",
        }
        mock_get_current_weather.return_value = {
            "temperature_f": "72",
            "condition": "Partly cloudy",
        }

        result = self.runner.invoke(cli, ["current"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output.strip(),
            "It is currently 72ºF, and Partly cloudy in Austin, Texas.",
        )
        mock_get_current_location.assert_called_once_with()
        mock_get_current_weather.assert_called_once_with("78701")

    @patch("weather.get_current_location")
    @patch("weather.get_current_weather")
    def test_current_without_zipcode_falls_back_to_city_state(self, mock_get_current_weather, mock_get_current_location):
        mock_get_current_location.return_value = {
            "city": "Austin",
            "state": "Texas",
        }
        mock_get_current_weather.return_value = {
            "temperature_f": "72",
            "condition": "Partly cloudy",
        }

        result = self.runner.invoke(cli, ["current"])

        self.assertEqual(result.exit_code, 0)
        mock_get_current_weather.assert_called_once_with("Austin,Texas")

    @patch("weather.get_location_by_zipcode")
    def test_current_with_unknown_zipcode(self, mock_get_location_by_zipcode):
        mock_get_location_by_zipcode.return_value = None

        result = self.runner.invoke(cli, ["current", "--zipcode", "00000"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Could not find location for zipcode 00000.", result.output)


class WeatherHelpersTests(unittest.TestCase):
    @patch("weather._request_json")
    def test_get_location_by_zipcode_returns_none_when_no_places(self, mock_request_json):
        mock_request_json.return_value = {}

        location = get_location_by_zipcode("10001")

        self.assertIsNone(location)

    @patch("weather._request_json")
    def test_get_current_weather_raises_on_incomplete_data(self, mock_request_json):
        mock_request_json.return_value = {"current_condition": [{"temp_F": "74", "weatherDesc": []}]}

        with self.assertRaises(WeatherError):
            get_current_weather("10001")


if __name__ == "__main__":
    unittest.main()
