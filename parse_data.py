"""
Parsed the data by collecting the verified packed from Que
and return the converted data as dict

"""

from utility_functions import *
import struct
from colorama import Back, Style, Fore

# status dict to map with code
STATUS_DICT = {'00': '3D mode',
               '01': 'waiting GPS time',
               '02': 'to hight PDOP',
               '03': 'no usable satellite',
               '04': 'receive only 1 satellite',
               '05': 'receive only 2 satellites',
               '06': '2D mode'}


def get_converted_data(que, data):
    if data is None:
        return

    q = que
    # get the verified packet from packet
    packet = data
    # convert to C type bytes
    lat = struct.unpack('>f', packet[2:6])[0]
    long = struct.unpack('>f', packet[6:10])[0]
    time = struct.unpack('>f', packet[10:14])[0]
    east_s = struct.unpack('>f', packet[14:18])[0]
    north_s = struct.unpack('>f', packet[18:22])[0]
    altitude = struct.unpack('>f', packet[22:26])[0]
    idn = packet[26:27]
    status = packet[27:28]
    checksum = packet[28:29]

    # calculate the check sum
    calculate_checksum = 0
    for i in packet[2:28]:
        calculate_checksum = i ^ calculate_checksum

    if calculate_checksum == checksum[0]:  # if a packet is verified via checksum
        lat_d = rad_degree(lat)  # convert rad to deg
        long_d = rad_degree(long)  # convert rad to deg
        resultant_s = get_resultant_s(east_s, north_s)  # convert east and north speed into resultant speed
        time_stamp = get_date(time)  # get the date from week sunday by adding time

        # map the hex code of status with status dict
        try:
            status_convert = STATUS_DICT.get(status.hex(), "None")
            status_convert = status.hex() + "(" + status_convert + ")"
        except TypeError:
            status_convert = status.hex() + "()"
        # print(Fore.GREEN + Style.BRIGHT + '*' * 30, 'Received TCP packet', '*' * 30)
        # print(Style.RESET_ALL)
        # packet_2 = display_packet(packet)
        #
        # print(Fore.RED + Style.BRIGHT + packet_2)
        # print(Style.RESET_ALL)
        #
        # print('Latitude:', lat)
        # print('Latitude:', long)
        # print('GPS_time(s):', time)
        # print('East S:', round(east_s, 3))
        # print('East S:', round(north_s, 3))
        # print('Altitude:', round(altitude, 3))
        # print('IDN:', idn.hex())
        # print('Status:', status.hex(), 'or', status_convert)
        # print('Checksum:', checksum.hex(), 'or', checksum[0])
        #
        # print('calculate checksum >>', calculate_checksum)
        # print('Checksum of messaeg verified', True)

        # creating the final valid packet, converted and verified
        final = {
            "lat": lat_d,
            "long": long_d,
            "gps_time": time,
            "resultant_s": resultant_s,
            "altitude": round(altitude, 3),
            "idn": idn[0],
            "idp": None,
            "status": status_convert,
            "checksum": checksum.hex(),
            "time_stamp": time_stamp}
        if not q.full():
            q.put(final)
