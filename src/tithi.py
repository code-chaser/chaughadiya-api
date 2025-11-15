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


def calculate_tithi(date: datetime.datetime, latitude: float, longitude: float):
    """
    Calculate the Tithi for a given date and location using Swiss Ephemeris.
    
    A Tithi is a lunar day in the Hindu calendar. It is the time taken for the 
    longitudinal angle between the Moon and the Sun to increase by 12 degrees.
    There are 30 Tithis in a lunar month.
    
    :param date: DateTime object with timezone information
    :param latitude: Latitude of the location
    :param longitude: Longitude of the location
    :return: Dictionary containing Tithi information
    """
    # Ensure date has timezone, default to UTC if not provided
    if date.tzinfo is None:
        date = pytz.UTC.localize(date)
    
    # Convert to UTC for calculations
    date_utc = date.astimezone(pytz.UTC)
    
    # Calculate Julian Day
    jd = swe.julday(date_utc.year, date_utc.month, date_utc.day, 
                    date_utc.hour + date_utc.minute/60.0 + date_utc.second/3600.0)
    
    # Calculate positions of Sun and Moon
    # Using geocentric coordinates
    # calc_ut returns a nested tuple: ((longitude, latitude, distance, speed_long, speed_lat, speed_dist), flags)
    sun_result = swe.calc_ut(jd, swe.SUN)
    moon_result = swe.calc_ut(jd, swe.MOON)
    
    # Extract longitude (first element of first tuple)
    sun_longitude = sun_result[0][0]
    moon_longitude = moon_result[0][0]
    
    # Calculate the elongation (difference in longitude)
    # Tithi is based on the angle between Moon and Sun
    elongation = moon_longitude - sun_longitude
    
    # Normalize to 0-360 range
    if elongation < 0:
        elongation += 360
    
    # Calculate Tithi number (each Tithi is 12 degrees)
    tithi_number = int(elongation / 12) + 1
    
    # Calculate progress within the current Tithi (0-1)
    tithi_progress = (elongation % 12) / 12
    
    # Ensure tithi_number is in valid range (1-30)
    if tithi_number > 30:
        tithi_number = tithi_number % 30
        if tithi_number == 0:
            tithi_number = 30
    
    # Get Tithi name
    tithi_name = __TITHI_NAMES[tithi_number - 1]
    
    # Determine Paksha (lunar phase)
    if tithi_number <= 15:
        paksha = 'Shukla Paksha (Waxing)'
    else:
        paksha = 'Krishna Paksha (Waning)'
    
    # Calculate approximate end time of current Tithi
    # The Moon moves about 13.2 degrees per day relative to the Sun
    # To cover remaining degrees in the Tithi (12 - current progress)
    remaining_degrees = 12 * (1 - tithi_progress)
    # Average angular velocity difference between Moon and Sun is about 0.55 degrees per hour
    hours_remaining = remaining_degrees / 0.55
    
    tithi_end_time = date_utc + datetime.timedelta(hours=hours_remaining)
    
    # Calculate start time of current Tithi
    hours_elapsed = (elongation % 12) / 0.55
    tithi_start_time = date_utc - datetime.timedelta(hours=hours_elapsed)
    
    # Calculate next Tithi
    next_tithi_number = (tithi_number % 30) + 1
    next_tithi_name = __TITHI_NAMES[next_tithi_number - 1]
    
    return {
        'tithi_number': tithi_number,
        'tithi_name': tithi_name,
        'paksha': paksha,
        'elongation_degrees': round(elongation, 2),
        'progress_percentage': round(tithi_progress * 100, 2),
        'start_time': tithi_start_time.isoformat(),
        'end_time': tithi_end_time.isoformat(),
        'next_tithi_number': next_tithi_number,
        'next_tithi_name': next_tithi_name,
        'significance': __TITHI_SIGNIFICANCE.get(tithi_name, 'Traditional lunar day'),
        'calculation_time': date_utc.isoformat()
    }


def get_tithi(date_str: str, latitude: float, longitude: float, timezone_str: str = 'UTC'):
    """
    Get Tithi information for a given date, location, and timezone.
    
    :param date_str: Date in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :param latitude: Latitude of the location
    :param longitude: Longitude of the location
    :param timezone_str: Timezone string (e.g., 'Asia/Kolkata', 'UTC')
    :return: Dictionary containing Tithi information
    """
    try:
        # Parse the date string
        if len(date_str) == 10:  # YYYY-MM-DD format
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            # Set to noon for better accuracy if time not provided
            date = date.replace(hour=12, minute=0, second=0)
        else:  # YYYY-MM-DD HH:MM:SS format
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        
        # Apply timezone
        tz = pytz.timezone(timezone_str)
        date = tz.localize(date)
        
        # Calculate Tithi
        result = calculate_tithi(date, latitude, longitude)
        
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
                             longitude: float, timezone_str: str = 'UTC'):
    """
    Get Tithi information for a range of dates.
    
    :param start_date: Start date in format YYYY-MM-DD
    :param end_date: End date in format YYYY-MM-DD
    :param latitude: Latitude of the location
    :param longitude: Longitude of the location
    :param timezone_str: Timezone string
    :return: List of dictionaries containing Tithi information for each day
    """
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    results = []
    current = start
    
    while current <= end:
        date_str = current.strftime('%Y-%m-%d')
        tithi_info = get_tithi(date_str, latitude, longitude, timezone_str)
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
    
    result = get_tithi(test_date, test_lat, test_lon, test_tz)
    
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

