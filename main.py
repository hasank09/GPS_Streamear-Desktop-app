"""
Main entry point for the app
Stream the data from GPS Server via TCP "localhost" port:4001


Created on 04 Mar 2021

"""

from GPS_stream_test import Stream as Stream
# from GPS_stream import Stream as Stream
from parse_data import get_converted_data
import utility_functions as ut_f
from write_csv import data_save
from AppGUI import GpsGUI
from tkinter import *
from pathlib import Path
import os
from queue import Queue

q = Queue(maxsize=10)


def main():
    if directory_check():
        root = Tk()
        # passing all the required object to the app
        GpsGUI(root, que=q, stream=Stream, parser=get_converted_data, output_file=data_save)
        root.mainloop()


def directory_check():
    """
    Check for the following files:
    a. configurations (CSV File) -- with mapping and monitoring details
    b. setting (Json file) -- to make the setting persistent


    :return: False or True
    :rtype: bool
    """

    paths = [Path('./data/GPS_DATA/'), Path('./data/Configuration/')]
    current_directory = Path('./data')
    configuration_file = Path('./data/Configuration/IDN_Mapping.csv')
    setting_file = Path('./data/Configuration/settings_file.json')

    for i in paths:

        if not i.exists():
            # print(i)
            if not current_directory.exists():
                os.mkdir(current_directory.absolute())
            os.mkdir(i.absolute())

    if not configuration_file.exists():

        ut_f.template_config(map_file=True)
    if not setting_file.exists():
        ut_f.template_config(setting_file=True)

    return True


if __name__ == '__main__':
    main()
