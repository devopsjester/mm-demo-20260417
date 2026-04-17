import unittest
from unittest.mock import patch

from click.testing import CliRunner

from weather import cli


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
    def test_where_is_without_zipcode_when_location_missing(self, mock_get_current_location):
        mock_get_current_location.return_value = None

        result = self.runner.invoke(cli, ["where-is"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Unable to determine current location.", result.output)


if __name__ == "__main__":
    unittest.main()
