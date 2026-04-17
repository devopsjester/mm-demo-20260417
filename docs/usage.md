# Weather CLI App — Usage Guide

The **weather** CLI application is a Python command-line tool that lets you look up location information and current weather conditions by zip code or by your current location.

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/devopsjester/mm-demo-20260417.git
   cd mm-demo-20260417
   ```

2. **Install dependencies:**

   ```bash
   python3 -m pip install -r requirements.txt
   ```

   The `requirements.txt` file includes all necessary packages, notably the [Click](https://click.palletsprojects.com/) CLI framework.

3. **(Optional) Install the package locally:**

   ```bash
   pip install .
   ```

   This makes the `weather` command available system-wide.

## Commands

### `where-is` — Look up a location

Displays the city and state for a given location.

**Usage:**

```bash
# Look up a specific zip code
weather where-is --zipcode 90210

# Detect your current location automatically
weather where-is
```

**Options:**

| Option              | Description                                      | Required |
|---------------------|--------------------------------------------------|----------|
| `--zipcode <zip>`   | A US zip code to look up                         | No       |

**Example output:**

```
90210 is in Beverly Hills, California.
```

If no zip code is provided, the app attempts to determine your current location:

```
Your current location is San Francisco, California.
```

---

### `current` — Get current weather conditions

Displays the current temperature (in Fahrenheit) and weather conditions for a given location.

**Usage:**

```bash
# Get weather for a specific zip code
weather current --zipcode 10001

# Get weather for your current location
weather current
```

**Options:**

| Option              | Description                                      | Required |
|---------------------|--------------------------------------------------|----------|
| `--zipcode <zip>`   | A US zip code to look up weather for             | No       |

**Example output:**

```
It is currently 72ºF, and Partly Cloudy in New York, New York.
```

If no zip code is provided, the app uses your current location:

```
It is currently 58ºF, and Foggy in San Francisco, California.
```

## Error Handling

The app provides informative error messages when something goes wrong:

- **Invalid zip code** — If the zip code format is invalid or not recognized, the app will display an error message asking you to provide a valid 5-digit US zip code.
- **API failures** — If the weather or geolocation API is unreachable, the app will notify you that data could not be retrieved.
- **Location detection failure** — If automatic location detection fails, the app will prompt you to provide a zip code manually using the `--zipcode` option.

## Notes

- All temperatures are displayed in Fahrenheit (imperial units).
- The app uses free, publicly available APIs that do not require API keys or registration.
- If no `--zipcode` is supplied, the app relies on IP-based geolocation to determine your current location, which may not always be precise (for example, when using a VPN).
