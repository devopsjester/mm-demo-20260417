# Weather CLI

A small Python CLI app for looking up US location and weather details.

## Requirements
- Python 3.7+

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage
```bash
python3 weather.py where-is --zipcode 10001
python3 weather.py where-is
python3 weather.py current --zipcode 10001
python3 weather.py current
```

## Notes
- `where-is` and `current` both accept an optional `--zipcode` (5-digit US zip).
- Without `--zipcode`, the app attempts to detect your current location by IP.
- The app uses free keyless APIs:
  - `api.zippopotam.us` for zipcode → city/state lookup
  - `ipapi.co` for IP-based location
  - `wttr.in` for current weather conditions
