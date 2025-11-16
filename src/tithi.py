import datetime
import pytz
try:
    import swisseph as swe
except ImportError:
    import ephem as swe  # Fallback if swisseph not available

# Tithi names (30 Tithis in a lunar month)
# 15 in Shukla Paksha (waxing moon) and 15 in Krishna Paksha (waning moon)
__TITHI_NAMES = [
    # Shukla Paksha (Waxing Moon - Days 1-15)
    'Pratipada (Shukla)',      # 1
    'Dwitiya (Shukla)',        # 2
    'Tritiya (Shukla)',        # 3
    'Chaturthi (Shukla)',      # 4
    'Panchami (Shukla)',       # 5
    'Shashthi (Shukla)',       # 6
    'Saptami (Shukla)',        # 7
    'Ashtami (Shukla)',        # 8
    'Navami (Shukla)',         # 9
    'Dashami (Shukla)',        # 10
    'Ekadashi (Shukla)',       # 11
    'Dwadashi (Shukla)',       # 12
    'Trayodashi (Shukla)',     # 13
    'Chaturdashi (Shukla)',    # 14
    'Purnima',                 # 15 - Full Moon
    # Krishna Paksha (Waning Moon - Days 16-30)
    'Pratipada (Krishna)',     # 16
    'Dwitiya (Krishna)',       # 17
    'Tritiya (Krishna)',       # 18
    'Chaturthi (Krishna)',     # 19
    'Panchami (Krishna)',      # 20
    'Shashthi (Krishna)',      # 21
    'Saptami (Krishna)',       # 22
    'Ashtami (Krishna)',       # 23
    'Navami (Krishna)',        # 24
    'Dashami (Krishna)',       # 25
    'Ekadashi (Krishna)',      # 26
    'Dwadashi (Krishna)',      # 27
    'Trayodashi (Krishna)',    # 28
    'Chaturdashi (Krishna)',   # 29
    'Amavasya'                 # 30 - New Moon
]

# Tithi meanings and significance
__TITHI_SIGNIFICANCE = {
    'Pratipada (Shukla)': 'Beginning, new ventures',
    'Dwitiya (Shukla)': 'Worship of deities',
    'Tritiya (Shukla)': 'Auspicious for spiritual activities',
    'Chaturthi (Shukla)': 'Worship of Ganesha',
    'Panchami (Shukla)': 'Worship of Saraswati',
    'Shashthi (Shukla)': 'Worship of Kartikeya',
    'Saptami (Shukla)': 'Worship of Sun',
    'Ashtami (Shukla)': 'Worship of Durga',
    'Navami (Shukla)': 'Worship of Durga',
    'Dashami (Shukla)': 'Auspicious for ceremonies',
    'Ekadashi (Shukla)': 'Fasting and spiritual practices',
    'Dwadashi (Shukla)': 'Worship of Vishnu',
    'Trayodashi (Shukla)': 'Auspicious for religious activities',
    'Chaturdashi (Shukla)': 'Worship of Shiva',
    'Purnima': 'Full Moon - highly auspicious',
    'Pratipada (Krishna)': 'Beginning of waning phase',
    'Dwitiya (Krishna)': 'Second day of waning',
    'Tritiya (Krishna)': 'Third day of waning',
    'Chaturthi (Krishna)': 'Fourth day of waning',
    'Panchami (Krishna)': 'Fifth day of waning',
    'Shashthi (Krishna)': 'Sixth day of waning',
    'Saptami (Krishna)': 'Seventh day of waning',
    'Ashtami (Krishna)': 'Worship of Krishna',
    'Navami (Krishna)': 'Ninth day of waning',
    'Dashami (Krishna)': 'Tenth day of waning',
    'Ekadashi (Krishna)': 'Fasting and spiritual practices',
    'Dwadashi (Krishna)': 'Twelfth day of waning',
    'Trayodashi (Krishna)': 'Thirteenth day of waning',
    'Chaturdashi (Krishna)': 'Worship of Shiva',
    'Amavasya': 'New Moon - for ancestor worship'
}

SECONDS_PER_DAY = 86400.0
JULIAN_DAY_UNIX_EPOCH = 2440587.5
DEFAULT_ELEVATION_METERS = 0.0

_REQUIRED_SWE_ATTRS = ('calc_ut', 'julday', 'set_topo')
_missing_attrs = [attr for attr in _REQUIRED_SWE_ATTRS if not hasattr(swe, attr)]
if _missing_attrs:
    raise ImportError(
        f"Swiss Ephemeris with topocentric support is required. Missing attributes: {_missing_attrs}"
    )

if not all(hasattr(swe, flag) for flag in ('FLG_SWIEPH', 'FLG_TOPOCTR', 'FLG_SPEED')):
    raise ImportError("Swiss Ephemeris build lacks required flag constants for topocentric calculations.")

_SWE_FLAGS = swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_SPEED


def _normalize_angle(value: float) -> float:
    return value % 360.0


def _angle_diff(angle: float, target: float) -> float:
    """
    Signed difference between two angles (in degrees) constrained to [-180, 180).
    Positive value means `angle` is ahead of `target`.
    """
    return ((angle - target + 180.0) % 360.0) - 180.0


def _jd_to_datetime(jd: float) -> datetime.datetime:
    seconds = (jd - JULIAN_DAY_UNIX_EPOCH) * SECONDS_PER_DAY
    return datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC) + datetime.timedelta(seconds=seconds)


def _get_elongation(jd: float) -> float:
    """
    Compute the topocentric elongation (Moon - Sun) in degrees for the given Julian Day.
    """
    moon_result = swe.calc_ut(jd, swe.MOON, _SWE_FLAGS)
    sun_result = swe.calc_ut(jd, swe.SUN, _SWE_FLAGS)

    moon_longitude = moon_result[0][0] % 360.0
    sun_longitude = sun_result[0][0] % 360.0

    return _normalize_angle(moon_longitude - sun_longitude)


def _bracket_tithi_boundary(jd_reference: float, target_angle: float, direction: int,
                            step_hours: float = 1.0, max_hours: float = 72.0):
    """
    Step forward/backward in time to bracket the instant when the elongation equals `target_angle`.
    Returns a tuple (jd_low, jd_high) such that the boundary lies within.
    """
    if direction == 0:
        raise ValueError("direction must be +1 or -1")

    step_days = (step_hours / 24.0) * direction
    elapsed_hours = 0.0

    prev_jd = jd_reference
    prev_diff = _angle_diff(_get_elongation(prev_jd), target_angle)

    if abs(prev_diff) < 1e-6:
        return prev_jd, prev_jd

    max_steps = int(max_hours / step_hours) + 1

    for _ in range(max_steps):
        next_jd = prev_jd + step_days
        next_diff = _angle_diff(_get_elongation(next_jd), target_angle)

        if prev_diff * next_diff <= 0:
            jd_low, jd_high = (next_jd, prev_jd) if next_jd < prev_jd else (prev_jd, next_jd)
            return jd_low, jd_high

        prev_jd = next_jd
        prev_diff = next_diff
        elapsed_hours += step_hours

    raise RuntimeError("Failed to bracket Tithi boundary within the allowed search window.")


def _solve_tithi_boundary(jd_low: float, jd_high: float, target_angle: float,
                          tolerance_deg: float = 1e-4, max_iterations: int = 60) -> float:
    """
    Refine the Tithi boundary between jd_low and jd_high using bisection until the elongation
    matches target_angle within `tolerance_deg`.
    """
    diff_low = _angle_diff(_get_elongation(jd_low), target_angle)
    diff_high = _angle_diff(_get_elongation(jd_high), target_angle)

    if abs(diff_low) < tolerance_deg:
        return jd_low
    if abs(diff_high) < tolerance_deg:
        return jd_high

    if diff_low * diff_high > 0:
        raise RuntimeError("Provided bracket does not contain a root.")

    for _ in range(max_iterations):
        mid_jd = 0.5 * (jd_low + jd_high)
        diff_mid = _angle_diff(_get_elongation(mid_jd), target_angle)

        if abs(diff_mid) < tolerance_deg:
            return mid_jd

        if diff_low * diff_mid <= 0:
            jd_high = mid_jd
            diff_high = diff_mid
        else:
            jd_low = mid_jd
            diff_low = diff_mid

    return 0.5 * (jd_low + jd_high)


def _find_tithi_boundary(jd_reference: float, target_angle: float, direction: int) -> float:
    """
    Convenience helper that brackets and refines the requested boundary.
    """
    jd_low, jd_high = _bracket_tithi_boundary(jd_reference, target_angle, direction)
    if jd_low == jd_high:
        return jd_low
    return _solve_tithi_boundary(jd_low, jd_high, target_angle)


def calculate_tithi(date: datetime.datetime, latitude: float, longitude: float,
                    elevation_meters: float = DEFAULT_ELEVATION_METERS):
    """
    Calculate the Tithi for a given date and location using Swiss Ephemeris.
    
    A Tithi is a lunar day in the Hindu calendar. It is the time taken for the 
    longitudinal angle between the Moon and the Sun to increase by 12 degrees.
    There are 30 Tithis in a lunar month.
    
    :param date: DateTime object with timezone information
    :param latitude: Latitude of the location
    :param longitude: Longitude of the location
    :param elevation_meters: Observer elevation above sea level in meters
    :return: Dictionary containing Tithi information
    """
    if date.tzinfo is None:
        date = pytz.UTC.localize(date)

    local_tz = date.tzinfo
    date_utc = date.astimezone(pytz.UTC)

    swe.set_topo(longitude, latitude, elevation_meters)

    jd = swe.julday(
        date_utc.year,
        date_utc.month,
        date_utc.day,
        date_utc.hour + date_utc.minute / 60.0 + date_utc.second / 3600.0 + date_utc.microsecond / 3_600_000_000.0
    )

    elongation = _get_elongation(jd)
    tithi_index = int(elongation // 12)
    tithi_number = tithi_index + 1
    tithi_number = 30 if tithi_number == 31 else tithi_number

    lower_target = tithi_index * 12.0
    upper_target = lower_target + 12.0

    tithi_start_jd = _find_tithi_boundary(jd, lower_target, direction=-1)
    tithi_end_jd = _find_tithi_boundary(jd, upper_target, direction=1)

    tithi_start_utc = _jd_to_datetime(tithi_start_jd)
    tithi_end_utc = _jd_to_datetime(tithi_end_jd)

    tithi_duration_seconds = max((tithi_end_utc - tithi_start_utc).total_seconds(), 1.0)
    elapsed_seconds = (date_utc - tithi_start_utc).total_seconds()
    tithi_progress = max(0.0, min(1.0, elapsed_seconds / tithi_duration_seconds))

    tithi_name = __TITHI_NAMES[tithi_number - 1]
    paksha = 'Shukla Paksha (Waxing)' if tithi_number <= 15 else 'Krishna Paksha (Waning)'

    next_tithi_number = (tithi_number % 30) + 1
    next_tithi_name = __TITHI_NAMES[next_tithi_number - 1]

    return {
        'tithi_number': tithi_number,
        'tithi_name': tithi_name,
        'paksha': paksha,
        'elongation_degrees': round(elongation, 6),
        'progress_percentage': round(tithi_progress * 100, 4),
        'start_time': tithi_start_utc.astimezone(local_tz).isoformat(),
        'end_time': tithi_end_utc.astimezone(local_tz).isoformat(),
        'start_time_utc': tithi_start_utc.isoformat(),
        'end_time_utc': tithi_end_utc.isoformat(),
        'next_tithi_number': next_tithi_number,
        'next_tithi_name': next_tithi_name,
        'duration_hours': round(tithi_duration_seconds / 3600.0, 4),
        'significance': __TITHI_SIGNIFICANCE.get(tithi_name, 'Traditional lunar day'),
        'calculation_time': date_utc.isoformat(),
        'observer': {
            'latitude': latitude,
            'longitude': longitude,
            'elevation_meters': elevation_meters
        }
    }


def get_tithi(date_str: str, latitude: float, longitude: float, timezone_str: str = 'UTC',
              elevation_meters: float = DEFAULT_ELEVATION_METERS):
    """
    Get Tithi information for a given date, location, and timezone.
    
    :param date_str: Date in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :param latitude: Latitude of the location
    :param longitude: Longitude of the location
    :param timezone_str: Timezone string (e.g., 'Asia/Kolkata', 'UTC')
    :param elevation_meters: Elevation of the observer above sea level in meters
    :return: Dictionary containing Tithi information
    """
    try:
        # Parse the date string
        if len(date_str) == 10:  # YYYY-MM-DD format
            date_obj = datetime.date.fromisoformat(date_str)
            date = datetime.datetime.combine(date_obj, datetime.time(hour=12))
        else:  # Expect ISO datetime format (e.g., YYYY-MM-DD HH:MM:SS)
            date = datetime.datetime.fromisoformat(date_str)
        
        # Apply timezone
        tz = pytz.timezone(timezone_str)
        date = tz.localize(date)
        
        # Calculate Tithi
        result = calculate_tithi(date, latitude, longitude, elevation_meters=elevation_meters)
        
        # Add input parameters to result
        result['input_date'] = date_str
        result['latitude'] = latitude
        result['longitude'] = longitude
        result['timezone'] = timezone_str
        
        return result
        
    except Exception as e:
        return {
            'error': f'Failed to calculate Tithi: {str(e)}',
            'input_date': date_str,
            'latitude': latitude,
            'longitude': longitude
        }


def get_tithi_for_date_range(start_date: str, end_date: str, latitude: float,
                             longitude: float, timezone_str: str = 'UTC',
                             elevation_meters: float = DEFAULT_ELEVATION_METERS):
    """
    Get Tithi information for a range of dates.
    
    :param start_date: Start date in format YYYY-MM-DD
    :param end_date: End date in format YYYY-MM-DD
    :param latitude: Latitude of the location
    :param longitude: Longitude of the location
    :param timezone_str: Timezone string
    :return: List of dictionaries containing Tithi information for each day
    """
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    
    results = []
    current = start
    
    while current <= end:
        date_str = current.isoformat()
        tithi_info = get_tithi(date_str, latitude, longitude, timezone_str, elevation_meters)
        results.append(tithi_info)
        current += datetime.timedelta(days=1)
    
    return results


if __name__ == '__main__':
    # Test the Tithi calculation
    print("Testing Tithi Calculation:")
    print("-" * 80)
    
    # Test for a specific date and location (New Delhi)
    test_date = "2025-11-15"
    test_lat = 28.6139
    test_lon = 77.2090
    test_tz = "Asia/Kolkata"
    test_elevation = 216  # Approx elevation for New Delhi in meters
    
    result = get_tithi(test_date, test_lat, test_lon, test_tz, test_elevation)
    
    print(f"Date: {result.get('input_date')}")
    print(f"Location: ({result.get('latitude')}, {result.get('longitude')})")
    print(f"Timezone: {result.get('timezone')}")
    print(f"\nTithi Number: {result.get('tithi_number')}")
    print(f"Tithi Name: {result.get('tithi_name')}")
    print(f"Paksha: {result.get('paksha')}")
    print(f"Progress: {result.get('progress_percentage')}%")
    print(f"Start Time: {result.get('start_time')}")
    print(f"End Time: {result.get('end_time')}")
    print(f"Next Tithi: {result.get('next_tithi_name')}")
    print(f"Significance: {result.get('significance')}")

