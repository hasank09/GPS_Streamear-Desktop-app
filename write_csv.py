import csv
from pathlib import Path
import os
import random as rnd


def data_save(data):
    """
    write the data into Excel file by appending at the end of data

    :param object dict: entire message as dic
    :return: True or False
    :rtype: Bool
    """

    file_path = Path('./data/GPS_DATA/log.csv')
    fieldnames = list(data.keys())

    def create_template():
        """
        When no Excel is found name "GPS_TCP.xlsx"
        will create a new one

        :return: None
        """
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def write_log():
        """
        append the data in the Excel as appending at the end of data
        """
        try:
            with open(file_path,'a',newline='') as csvfile:
                writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
                writer.writerow(data)
            return True
        except (PermissionError, FileNotFoundError) as err:
            print(err)
            print("Data Saving Error:Excel File")
            return False

    if not file_path.exists():
        create_template()

    if write_log():
        return True
    else:
        return False


if __name__ == '__main__':
    # self test
    for i in range(100):
        tem_data = {
            "lat": rnd.randint(1, 99),
            "long": rnd.randint(1, 99),
            "gps_time": rnd.randint(1, 99),
            "resultant_s": rnd.randint(1, 99),
            "altitude": rnd.randint(1, 99),
            "idn": rnd.randint(1, 99),
            "status": rnd.randint(1, 99),
            "checksum": rnd.randint(1, 99),
            "time_stamp": rnd.randint(1, 99)}
        data_save(tem_data)
