from tkinter import *
from tkinter.messagebox import showinfo
import ipaddress
import pandas as pd
import time
import json
from threading import Thread
from queue import Queue, Empty, Full
from pathlib import Path
import utility_functions as ut_f
from datetime import datetime, timezone

FONT = ('Arial', 12, 'normal')
FONT2 = ('Arial', 10, 'normal')
FONT3 = ('Arial', 14, 'bold')


class GpsGUI:

    def __init__(self, master, que, stream, parser, output_file):
        self.master = master  # Parent Window
        self.master.title('GPS STREAM')
        self.master.config(padx=20, pady=20)
        self.link_window = None
        # software setting parameters to make it persistent for every run - Start
        self._tcp_ip = None
        self._tcp_port = None
        self._json_update = None
        self._event_name = None
        self._event_location = None
        # software setting parameters to make it persistent for every run - End

        # initialize que to monitor the online status of the GPS - Start
        self._que_stop = Queue(maxsize=2)
        self._que_stop.put_nowait(False)
        # initialize que to monitor the online status of the GPS - End

        # all the input data to update from GUI - Start
        self._ip_input = None
        self._port_input = None
        self._event_name_input = None
        self._event_location_input = None
        self._json_update_input = None
        # all the input data to update from GUI - End

        # to track all the threading - Start
        self.stream_thread = None
        self.schedule_parsing_id = None
        self.schedule_status_id = None
        self.schedule_write_id = None
        self.schedule_json_id = None
        self.schedule_json_data_id = None
        # to track all the threading - End

        # Generic object to help in programming - Start
        self._event_start_time = None  # for json event recording
        self._event_end_time = None  # for json event recording
        self.df_mapping = None  # for delay monitoring this is pandas dataframe
        self.original_bg = None  # to restore the background of the data field to default
        self._latest_data_dict = dict()  # to capture the latest data between the defined frequency
        self._json_starters = []
        # Generic object to help in programming - End

        # to generate the widgets on GUI for the following attributes
        attr_names = ['lat', 'long', 'gps_time', 'resultant_s', 'altitude', 'idn',
                      'status', 'checksum', 'time_stamp']

        self.var_data_dict = dict()  # variable to track all attr for label on GUI
        self._q = que
        self._stream = stream(self._q, self._que_stop)  # func -> stream object for getting data from server
        self._parser = parser  # func-> to parse and convert the data
        self._out_data = output_file  # fun-> to save the logs into csv

        # Status for the gps
        gps_status_label = Label(master, text="-----", font=FONT3, width=10)
        gps_status_label.pack(side=TOP, expand=YES, fill=BOTH, padx=10, pady=10)
        self.gps_status = gps_status_label

        # add the label for all attr on GUI
        for i in attr_names:
            self.add_data_fields(i)

        # Buttons RWO-1
        row1_frame = Frame(self.master, height=50, pady=5)
        tcp_button = Button(row1_frame, text="Setting", font=FONT3, command=self.update_setting, width=10)
        tcp_button.pack(side=LEFT, expand=YES, fill=BOTH, padx=10)

        start_button = Button(row1_frame, text="Start Streaming", font=FONT3, command=self.start_streaming, width=14)
        start_button.pack(side=RIGHT, expand=YES, fill=BOTH, padx=10)
        row1_frame.pack(side=TOP, expand=YES, fill=BOTH)

        # Buttons RWO-2
        row2_frame = Frame(self.master, height=50)
        close_button = Button(row2_frame, text="Closed", font=FONT3, command=self.closed_app)
        close_button.pack(side=LEFT, expand=YES, fill=BOTH, padx=10)
        stop_button = Button(row2_frame, text="Stop Streaming", font=FONT3, command=self.stop_streaming, width=10)
        stop_button.pack(side=RIGHT, expand=YES, fill=BOTH, padx=10)
        row2_frame.pack(side=BOTTOM, expand=YES, fill=BOTH)

        self.original_bg = close_button.cget('background')
        self.get_setting()

    def add_data_fields(self, name='testing'):
        wdg_pd_x = 10
        wdg_pd_y = 5

        # Web frame Starts
        web_frame = Frame(self.master, borderwidth=3, relief=GROOVE)

        # Label
        attr_label = Label(web_frame, text=name + ':', font=('Arial', 12, 'normal'), width=10)
        attr_label.pack(side=LEFT, expand=YES, fill=BOTH, padx=wdg_pd_x, pady=wdg_pd_y)

        # Label
        value_label = Label(web_frame, text='----', font=('Arial', 12, 'bold'), width=20)
        value_label.pack(side=LEFT, expand=YES, fill=BOTH, padx=wdg_pd_x, pady=wdg_pd_y)
        self.var_data_dict[name] = value_label

        # Frame Ends
        web_frame.pack(side=TOP, expand=YES, fill=BOTH, pady=5)

    def start_streaming(self):

        if not self.check_configuration():
            return

        if isinstance(self.stream_thread, Thread):
            if self.stream_thread.is_alive():
                showinfo("STREAMING", message=f"An Streaming already configure Please stop that first")

                return

        for i in range(2):
            try:
                self._que_stop.get_nowait()
            except Empty:
                pass

        for i in range(2):
            try:
                self._que_stop.put_nowait(False)
            except Full:
                pass
        if (self._tcp_ip is not None) and (self._tcp_port is not None):
            stream_arg = (self._tcp_ip, self._tcp_port)
            self.stream_thread = Thread(target=self._stream.tcp_stream, args=stream_arg)
            self.stream_thread.start()
        else:
            showinfo(title="TCP Error", message="There is a error in the TCP IP or port setting please verify")

        self.get_setting()
        self.schedule_status()
        self.schedule_parsing()
        self.schedule_json_output()

    def stop_streaming(self):

        if not isinstance(self.stream_thread, Thread):
            return

        for i in range(2):
            try:
                self._que_stop.get_nowait()
            except Empty:
                pass
        for i in range(2):
            try:
                self._que_stop.put_nowait(True)
            except Full:
                pass

        self.master.after_cancel(self.schedule_parsing_id)
        self.master.after_cancel(self.schedule_status_id)
        try:
            self.master.after_cancel(self.schedule_write_id)
            self.master.after_cancel(self.schedule_json_id)
            self.master.after_cancel(self.schedule_json_data_id)
        except ValueError:
            pass
        self.stream_thread.join()

        for i in range(2):
            try:
                self._que_stop.get_nowait()
            except Empty:
                pass
        self.clear_que()
        self.reset_display()

    def schedule_status(self):
        if not self._stream.DEVICE_ONLINE:  # status of streaming tcp server
            self.gps_status.config(text="GPS Server - Offline", fg='red')
        else:
            self.gps_status.config(text="GPS Server - Online", fg='green')
        self.schedule_status_id = self.master.after(2000, self.schedule_status)

    def schedule_parsing(self):
        try:
            data = self._q.get_nowait()  # get parsed data
        except Empty:
            data = None

        if isinstance(data, dict):  # get the converted the data in dict
            data['idn'] = str(data['idn'])
            idn_map = self.df_mapping.loc[data['idn'], "IDP"]
            data['idp'] = idn_map
            self.schedule_json_data_id = self.master.after(500, lambda: self.schedule_json_data(data))
            self.calculate_delay(data)
            current_delay = self.df_mapping.loc[data['idn'], 'delay']
            color = self.get_color(data)
            # print('Current IDP>>', data['idp'], "Delay Calculated>>", current_delay, "Color>>", color)
            for (a, b) in data.items():
                if a == 'idp':
                    continue
                if a == 'idn':
                    if color:
                        self.var_data_dict[a].config(text=idn_map, bg=color)
                    else:
                        self.var_data_dict[a].config(text=idn_map, bg=self.original_bg)
                else:
                    self.var_data_dict[a].config(text=b)
            self.schedule_write_id = self.master.after(10, lambda: self.schedule_write_csv(data))

        else:  # when no data is available
            self.reset_display()

        self.schedule_parsing_id = self.master.after(2000, self.schedule_parsing)
        print("final_data>>", data)
        # print(self.df_mapping)

    def schedule_json_data(self, data):
        current_monitor_status = self.df_mapping.loc[data['idn'], 'monitor_status']
        if current_monitor_status.lower() == 'no':
            return

        data_dict_1 = dict()
        data_dict_2 = dict()
        # level_1
        data_dict_1['id'] = data['idn']
        data_dict_1['name'] = data['idp']
        # level_2
        data_dict_2['time'] = data['time_stamp']
        data_dict_2['lng'] = data['long']
        data_dict_2['lat'] = data['lat']
        data_dict_2['elv'] = data['altitude']
        data_dict_2['speed'] = data['resultant_s']
        data_dict_1['current'] = data_dict_2
        self._latest_data_dict[data['idn']] = data_dict_1

    def schedule_json_output(self):

        if self._event_start_time is None:
            self._event_start_time = datetime.now()
            self.schedule_json_id = self.master.after(self._json_update * 1000, self.schedule_json_output)
            return
        else:
            collected_data = self.update_starters()
            # self._latest_data_dict.clear()
            self._event_end_time = datetime.now()
            json_template = {'name': self._event_name, 'location': self._event_location,
                             'startTime': self._event_start_time.isoformat(),
                             'endTime': self._event_end_time.isoformat(),
                             'starters': collected_data}
            file_path = Path('./data/GPS_DATA/out_json.json')
            with open(file_path, 'w') as file:
                file.write(json.dumps(json_template, indent=4))

        self._event_start_time = datetime.now()
        self.rest_json_dict()
        self.schedule_json_id = self.master.after(self._json_update * 1000, self.schedule_json_output)

    def rest_json_dict(self):
        null_dict = {
            'time': None,
            'lng': None,
            'lat': None,
            'elv': None,
            'speed': None,
        }

        self._json_starters = []
        for i in self.df_mapping.iterrows():
            monitor_status = i[1]['monitor_status']
            if monitor_status.lower() == 'no':
                continue
            data_dict_1 = dict()
            data_dict_1['id'] = i[0]
            data_dict_1['name'] = i[1]['IDP']
            data_dict_1['current'] = null_dict
            self._json_starters.append(data_dict_1)

    def update_starters(self):
        for index, i in enumerate(self._json_starters):
            current_id = i['id']
            if current_id in self._latest_data_dict:
                self._json_starters[index] = self._latest_data_dict[current_id]
            # else:
            #     self._json_starters[index] = None

        return self._json_starters

    def schedule_write_csv(self, data):
        write_data = data
        try:
            data_write_check = self._out_data(write_data)  # same data to write into csv
            if not data_write_check:  # if csv file have error
                raise FileExistsError
        except FileExistsError:
            self.stop_streaming()
            showinfo("Out Put Error", message="Excel file is opened/accessed by another program, Please check"
                                              "\nGPS Data Streaming is closing now")
            self.master.destroy()

    def update_setting(self):

        self.stop_streaming()

        self.link_window = Toplevel(self.master)
        self.link_window.config(pady=10)

        # ip_address frame
        tcp_frame = Frame(self.link_window, relief=GROOVE, borderwidth=5, height=5)
        tcp_frame.propagate()

        Label(tcp_frame, text='TCP Setting', font=('Arial', 10, 'bold'), pady=1).place(relx=0.1, rely=-0.14, anchor=NW)

        # ip_address
        self._ip_input = Entry(tcp_frame, width=15, font=('Arial', 10, 'normal'))
        self._ip_input.insert(0, self._tcp_ip)
        self._ip_input.grid(row=0, column=0, padx=5, pady=10)
        ip_address_label = Label(tcp_frame, text="IP Address", font=('Arial', 10, 'normal'))
        ip_address_label.grid(row=0, column=1, padx=0, pady=0, sticky=N + S + W)

        # port
        self._port_input = Entry(tcp_frame, width=15, font=('Arial', 10, 'normal'))
        self._port_input.insert(0, str(self._tcp_port))
        self._port_input.grid(row=1, column=0, padx=5, pady=5)
        port_label = Label(tcp_frame, text="Port", font=('Arial', 10, 'normal'))
        port_label.grid(row=1, column=1, padx=0, pady=0, sticky=N + S + W)
        tcp_frame.grid(row=0, column=0, padx=10, pady=5)

        # Event frame
        event_frame = Frame(self.link_window, relief=GROOVE, borderwidth=5, height=5, width=50)

        Label(event_frame, text='Event Setting', font=('Arial', 10, 'bold'), pady=1).place(relx=0.1, rely=-0.11,
                                                                                           anchor=NW)
        # event name
        self._event_name_input = Entry(event_frame, width=15, font=('Arial', 10, 'normal'))
        self._event_name_input.insert(0, self._event_name)
        self._event_name_input.grid(row=0, column=0, padx=5, pady=10)
        event_name_label = Label(event_frame, text="Event Name", font=('Arial', 10, 'normal'))
        event_name_label.grid(row=0, column=1, padx=0, pady=0, sticky=N + S + W)

        # event location
        self._event_location_input = Entry(event_frame, width=15, font=('Arial', 10, 'normal'))
        self._event_location_input.insert(0, self._event_location)
        self._event_location_input.grid(row=1, column=0, padx=5, pady=5)
        event_location_label = Label(event_frame, text="Event Location", font=('Arial', 10, 'normal'))
        event_location_label.grid(row=1, column=1, padx=0, pady=0, sticky=N + S + W)

        # update time
        self._json_update_input = Entry(event_frame, width=15, font=('Arial', 10, 'normal'))
        self._json_update_input.insert(0, str(self._json_update))
        self._json_update_input.grid(row=2, column=0, padx=5, pady=5)
        json_update_abel = Label(event_frame, text="Update Time(S)", font=('Arial', 10, 'normal'))
        json_update_abel.grid(row=2, column=1, padx=0, pady=0, sticky=N + S + W)

        event_frame.grid(row=1, column=0, padx=10, pady=5)

        # Buttons tcp window
        button_frame = Frame(self.link_window, height=30, pady=10)
        tcp_update_button = Button(button_frame, text="Update", font=FONT2, command=self.read_setting)
        tcp_update_button.grid(row=0, column=0, padx=5, pady=5)
        close_button = Button(button_frame, text="closed", font=FONT2, command=self.link_window.destroy)
        close_button.grid(row=0, column=1, padx=5, pady=5)

        button_frame.grid(row=3, column=0, padx=5, pady=5, sticky=N + W)

    def read_setting(self):
        try:
            self._tcp_ip = ipaddress.ip_address(self._ip_input.get()).exploded
            self._tcp_port = int(self._port_input.get())

            self._event_name = self._event_name_input.get()
            self._event_location = self._event_location_input.get()
            self._json_update = int(self._json_update_input.get())

            self.set_setting()

            if self._tcp_port > 65535 or self._tcp_port <= 1023 or self._tcp_port < 0:
                raise ValueError("Port Number is not valid, port: 1023 > Port <=65535")

        except (ValueError, TypeError) as tcp_error:

            showinfo("IP error", message=f"Please check the IP address and Port\n"
                                         f"{tcp_error}")
            return

    def closed_app(self):
        self.stop_streaming()
        self.master.destroy()

    def clear_que(self):
        while not self._q.empty():
            try:
                self._q.get()
            except:
                break

        self.gps_status.config(text="GPS Server - Offline", fg='red')
        for no_value in self.var_data_dict.values():
            no_value.config(text='-------')

    def check_configuration(self):
        try:
            paths = Path('./data/Configuration/')
            all_csv = list(paths.glob('*.csv'))
            if paths.exists():
                df_mapping = None
                for file in all_csv:
                    if file.name == 'IDN_Mapping.csv':
                        df_mapping = pd.read_csv(file, index_col='IDN')
                        df_mapping['start_time'] = df_mapping.index * 0
                        df_mapping['start_time'] = df_mapping['start_time'].astype('float')
                        df_mapping['delay'] = df_mapping['start_time'] * 0
                        df_mapping.index = df_mapping.index.astype('str')
                        df_mapping.rename(columns={'json_include': 'monitor_status'},inplace=True)
                        self.df_mapping = df_mapping
                        self.rest_json_dict()

                if df_mapping is None:
                    showinfo("Config File", message="Mapping config file not Found, created template")
                    ut_f.template_config(map_file=True)
            else:
                raise NotADirectoryError("Configuration folder not found please restart the program")
        except NotADirectoryError as err:
            showinfo("Config File", message=f"{err}")
            return False
        return True

    def calculate_delay(self, packet):
        data = packet

        if self.df_mapping.loc[data['idn'], 'start_time'] == 0:
            self.df_mapping.loc[data['idn'], 'start_time'] = time.time()  # start time
        else:
            self.df_mapping.loc[data['idn'], 'delay'] = time.time() - self.df_mapping.loc[
                data['idn'], 'start_time']  # delay
            self.df_mapping.loc[data['idn'], 'start_time'] = time.time()  # record new reading

    def get_color(self, data):
        data = data
        if self.df_mapping.loc[data['idn'], 'delay'] >= self.df_mapping.loc[data['idn'], 'r_th']:
            return 'RED'
        elif self.df_mapping.loc[data['idn'], 'delay'] >= self.df_mapping.loc[data['idn'], 'y_th']:
            return 'YELLOW'
        else:
            return None

    def get_setting(self):
        setting_parameters = {'ip_address', 'port', 'event_name', 'event_location', 'json_update'}
        with open('./data/Configuration/settings_file.json') as file:
            setting_data = json.loads(file.read())

        if setting_parameters == set(setting_data.keys()):
            self._tcp_ip = setting_data.get('ip_address', None)
            self._tcp_port = setting_data.get('port', None)
            self._event_name = setting_data.get('event_name', None)
            self._event_location = setting_data.get('event_location', None)
            self._json_update = setting_data.get('json_update', None)
        else:
            showinfo("Setting Error", message="there is error in setting json, setting has been restore to default")
            ut_f.template_config(setting_file=True)
            self.master.destroy()
        # print(setting_data)

    def set_setting(self):

        setting_dict = {
            'ip_address': self._tcp_ip,
            'port': self._tcp_port,
            'event_name': self._event_name,
            'event_location': self._event_location,
            'json_update': self._json_update,

        }
        setting_json = json.dumps(setting_dict)
        with open('./data/Configuration/settings_file.json', 'w') as file:
            file.write(setting_json)

    def reset_display(self):
        for no_value in self.var_data_dict.values():
            no_value.config(text='-------', bg=self.original_bg)
