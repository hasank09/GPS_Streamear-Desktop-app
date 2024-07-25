"""
Misc helping function like conversion etc.

"""

from datetime import date, timedelta, datetime
import math
import pandas as pd
import string
import random
import json


def get_date(time_input):
    """
    get the time in seconds from this week Sunday and calculate
    time stamp
    :time_input: time in seconds from Sunday
    :return: time stamp
    :rtype: str
    """
    try:
        today_date = date.today()
        week_day = today_date.isoweekday()
        # identity sunday
        if week_day <= 6:
            week_sunday = today_date - timedelta(days=week_day)
        elif week_day == 7:
            week_sunday = today_date
        else:
            week_sunday = today_date
        new_date = datetime.fromisoformat(week_sunday.isoformat())
        new_date = new_date + timedelta(seconds=time_input)

        return new_date.isoformat()
    except (OverflowError, ValueError, OSError):
        return ""


def rad_degree(radians: float):
    """
    convert a radian angle to a degree angle

    :param radians: angle in radian
    :return: angle in degrees
    :rtype: float
    """
    return (radians * 180) / math.pi


def get_resultant_s(east_s, north_s):
    """
    convert east_speed and north speed into resultant speed
    using pythagoras theorem

    :param north_s: speed in m/s
    :param east_s: speed in m/s
    :return: resultant speed m/s
    :rtype: float
    """

    resultant_s = math.sqrt(east_s ** 2 + north_s ** 2)
    return resultant_s


def display_packet(packet):
    """
    to test the packet in hex format

    :param packet: object bytearray: packet as bytearray
    :return: packet in as hex string
    :rtype: str
    """
    try:
        start = '10ff'
        lat = packet[2:6].hex()
        long = packet[6:10].hex()
        time = packet[10:14].hex()
        east_s = packet[14:18].hex()
        north_s = packet[18:22].hex()
        altitude = packet[22:26].hex()
        idn = packet[26:27].hex()
        status = packet[27:28].hex()
        checksum = packet[28:29].hex()
        end = '1003'
    except:
        start = lat = long = time = east_s = north_s = altitude = idn = status = checksum = end = ''
        packet = []

    if packet:

        display = f"{start} {lat} {long} {time} {east_s} {north_s} {altitude} {idn} {status} {checksum} {end}"
        # print(display)
        return display
    else:
        return ""


def template_config(map_file=False, setting_file=False):
    if map_file:
        mapping_dict = dict()
        for i in zip(range(1, 16), string.ascii_uppercase[:16]):
            delay_default = random.choice([5, 10, 15, 20])
            mapping_dict[i[0]] = [i[1] + str(i[0]), i[0], delay_default, delay_default + 5, 'Yes']

        df_mapping = pd.DataFrame.from_dict(mapping_dict, orient='index', columns=['IDP', 'IDN', 'y_th', 'r_th',
                                                                                   'json_include'])
        df_mapping.to_csv('./data/Configuration/IDN_Mapping.csv', index=False)
    if setting_file:
        setting_dict = {
            'ip_address': '127.0.0.1',
            'port': 4001,
            'json_update': 10,
            'event_name': 'Test Event1',
            'event_location': 'Test Location1'
        }
        setting_json = json.dumps(setting_dict,indent=4)
        with open('./data/Configuration/settings_file.json', 'w') as file:
            file.write(setting_json)


if __name__ == '__main__':
    # template_config(setting_file=True)
    template_config(map_file=True)
