import datetime
from suntime import Sun, SunTimeException

__DAYS_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednessday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}
__MUHURATS = {
    0: 'Udveg',
    1: 'Kaal',
    2: 'Rog',
    3: 'Chal',
    4: 'Labh',
    5: 'Amrit',
    6: 'Shubh'
}
__CHAUGHADIYA = {
    0: [
        [ 5, 1, 6, 2, 0, 3, 4, 5 ],
        [ 3, 2, 1, 4, 0, 6, 5, 3 ]
    ],
    1: [
        [ 2, 0, 3, 4, 5, 1, 6, 2 ],
        [ 1, 4, 0, 6, 5, 3, 2, 1 ]
    ],
    2: [
        [ 4, 5, 1, 6, 2, 0, 3, 4 ],
        [ 0, 6, 5, 3, 2, 1, 4, 0 ]
    ],
    3: [
        [ 6, 2, 0, 3, 4, 5, 1, 6 ],
        [ 5, 3, 2, 1, 4, 0, 6, 5 ]
    ],
    4: [
        [ 3, 4, 5, 1, 6, 2, 0, 3 ],
        [ 2, 1, 4, 0, 6, 5, 3, 2 ]
    ],
    5: [
        [ 1, 6, 2, 0, 3, 4, 5, 1 ],
        [ 4, 0, 6, 5, 3, 2, 1, 4 ]
    ],
    6: [
        [ 0, 3, 4, 5, 1, 6, 2, 0 ],
        [ 6, 5, 3, 2, 1, 4, 0, 6 ]
    ]
}


"""
There are 8 muhurats between every sunrise and sunset.
The time between sunrise and sunset is divided into 8 equal parts
and each part is known as a Muhurat.
"""

def print_daywise_chaughadiya():
    print("Day Chaughadiya: ")
    print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}".format("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))
    for i in range(8):
        print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}".format(
            __MUHURATS[__CHAUGHADIYA[0][0][i]],
            __MUHURATS[__CHAUGHADIYA[1][0][i]],
            __MUHURATS[__CHAUGHADIYA[2][0][i]],
            __MUHURATS[__CHAUGHADIYA[3][0][i]],
            __MUHURATS[__CHAUGHADIYA[4][0][i]],
            __MUHURATS[__CHAUGHADIYA[5][0][i]],
            __MUHURATS[__CHAUGHADIYA[6][0][i]]
        ))

    print("Night Chaughadiya: ")
    print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}".format("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))
    for i in range(8):
        print("{:<7} {:<7} {:<7} {:<7} {:<7} {:<7} {:<7}".format(
            __MUHURATS[__CHAUGHADIYA[0][1][i]],
            __MUHURATS[__CHAUGHADIYA[1][1][i]],
            __MUHURATS[__CHAUGHADIYA[2][1][i]],
            __MUHURATS[__CHAUGHADIYA[3][1][i]],
            __MUHURATS[__CHAUGHADIYA[4][1][i]],
            __MUHURATS[__CHAUGHADIYA[5][1][i]],
            __MUHURATS[__CHAUGHADIYA[6][1][i]]
        ))
def get_daywise_chaughadiya():
    day_chaughadiya = []
    night_chaughadiya = []
    for i in range(8):
        day_chaughadiya.append([
            __MUHURATS[__CHAUGHADIYA[0][0][i]],
            __MUHURATS[__CHAUGHADIYA[1][0][i]],
            __MUHURATS[__CHAUGHADIYA[2][0][i]],
            __MUHURATS[__CHAUGHADIYA[3][0][i]],
            __MUHURATS[__CHAUGHADIYA[4][0][i]],
            __MUHURATS[__CHAUGHADIYA[5][0][i]],
            __MUHURATS[__CHAUGHADIYA[6][0][i]]
        ])
        night_chaughadiya.append([
            __MUHURATS[__CHAUGHADIYA[0][1][i]],
            __MUHURATS[__CHAUGHADIYA[1][1][i]],
            __MUHURATS[__CHAUGHADIYA[2][1][i]],
            __MUHURATS[__CHAUGHADIYA[3][1][i]],
            __MUHURATS[__CHAUGHADIYA[4][1][i]],
            __MUHURATS[__CHAUGHADIYA[5][1][i]],
            __MUHURATS[__CHAUGHADIYA[6][1][i]]
        ])
    return day_chaughadiya, night_chaughadiya
        

def get_chaughadiya(date: str, latitude: float, longitude: float):
    """
    Returns the chaughadiya for the given date.
    {
        'date': '%Y-%m-%d',
        'sunrise-time': '%H:%M:%S',
        'sunset-time': '%H:%M:%S',
        'day-muhurat-length': '%H:%M:%S',
        'night-muhurat-length': '%H:%M:%S',
        'chaughdiya': [
            {
                'muhurat': '',
                'start-time': '%H:%M:%S',
                'end-time': '%H:%M:%S',
            }
        ]
    }
    """
    # Converting the date string to datetime object.
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    # Fetching the sunrise and sunset time for the given date.
    sun = Sun(latitude, longitude)
    sunrise = sun.get_sunrise_time(date)
    sunset = sun.get_sunset_time(date)
    # Fetching sunset time of the previous day,
    # and sunrise time of the next day.
    prev_date = date - datetime.timedelta(days=1)
    next_date = date + datetime.timedelta(days=1)
    prev_sunset = sun.get_sunset_time(prev_date)
    next_sunrise = sun.get_sunrise_time(next_date)
    # Calculating the length of muhurats (3 kinds).
    part_1_muhurat_length = (sunrise - prev_sunset).total_seconds() / 8
    part_2_muhurat_length = (sunset - sunrise).total_seconds() / 8
    part_3_muhurat_length = (next_sunrise - sunset).total_seconds() / 8
    # Chaughadiya for the three parts.
    part_1_chaughadiya = []
    part_2_chaughadiya = []
    part_3_chaughadiya = []
    # Calculating the chaughadiya.
    for i in range(8):
        # Calculating the start time of the muhurat.
        part_1_start_time = prev_sunset + datetime.timedelta(seconds=part_1_muhurat_length * i)
        part_2_start_time = sunrise + datetime.timedelta(seconds=part_2_muhurat_length * i)
        part_3_start_time = sunset + datetime.timedelta(seconds=part_3_muhurat_length * i)
        # Calculating the end time of the muhurat.
        part_1_end_time = prev_sunset + datetime.timedelta(seconds=part_1_muhurat_length * (i + 1))
        part_2_end_time = sunrise + datetime.timedelta(seconds=part_2_muhurat_length * (i + 1))
        part_3_end_time = sunset + datetime.timedelta(seconds=part_3_muhurat_length * (i + 1))
        # Appending the muhurat to the chaughadiya.
        part_1_chaughadiya.append({
            'muhurat': __MUHURATS[__CHAUGHADIYA[date.weekday()][0][i]],
            'start-time': part_1_start_time.strftime('%H:%M:%S'),
            'end-time': part_1_end_time.strftime('%H:%M:%S')
        })
        part_2_chaughadiya.append({
            'muhurat': __MUHURATS[__CHAUGHADIYA[date.weekday()][1][i]],
            'start-time': part_2_start_time.strftime('%H:%M:%S'),
            'end-time': part_2_end_time.strftime('%H:%M:%S')
        })
        part_3_chaughadiya.append({
            'muhurat': __MUHURATS[__CHAUGHADIYA[date.weekday()][0][i]],
            'start-time': part_3_start_time.strftime('%H:%M:%S'),
            'end-time': part_3_end_time.strftime('%H:%M:%S')
        })
    # Merging all 3 parts of chaughadiya.
    chaughadiya = part_1_chaughadiya + part_2_chaughadiya + part_3_chaughadiya
    # Returning the chaughadiya.
    response = {
        'date': date.strftime('%Y-%m-%d'),
        'sunrise-time': sunrise.strftime('%H:%M:%S'),
        'sunset-time': sunset.strftime('%H:%M:%S'),
        'day-muhurat-length': str(datetime.timedelta(seconds=part_2_muhurat_length)),
        'night-muhurat-length': str(datetime.timedelta(seconds=part_1_muhurat_length + part_3_muhurat_length)),
        'chaughadiya': chaughadiya
    }
    return response

def get_muhurat(timestamp: str, latitude: float, longitude: float):
    """
    Returns the muhurat for the given timestamp,
    along with the chaughadiya for the given date.
    """
    chaughadiya = get_chaughadiya(timestamp[:10], latitude, longitude)
    timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    # Converting the timestamp to seconds.
    timestamp = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
    # Calculating the muhurat.
    


if __name__ == '__main__':
    print(get_chaughadiya("2023-12-17", 27.989871, 73.303466))