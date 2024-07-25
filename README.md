# GPS_Streamear-Desktop-app

To Develop the Desktop Based software which enables the customer to integrate the GPS data to another subsystem.
data is related with rider / cyclst <br>
GPS data format is customized.
### Requirment:
<p>
The goal of this project is to develop a software solution for acquiring, processing, and outputting GPS data streams. The software will handle various data acquisition methods, parse and format the GPS data, convert it into specified units of measurement, and output the processed data in an Excel-compatible format
</p>
<br>
Following is the main component to the systems:
<ul>
1. Interface with GPS: 
  <ul>
  <li>using TCP interface connect with the GPS and stream data <br></li>
  <li>configure the json update time</li>
  <li>start and stop the streaming</li>
</ul>
2. GUI:<br>
<ul>
  <li>using GUI select the TCP ip and port data</li>
  <li>display the parsed data on GUI</li>
  <li>highlight the rider ID if data comes after certian delay based on the configuration file</li>
</ul>
3. Data processing:  Implement robust data processing to format GPS data according to specified requirements and save it in usable formats such as Excel, CSV, database, JSON, etc. <br>
  GPS_Packet Document >>(https://drive.google.com/file/d/1WF6wvIu_ae95DhYlU0LC0EkmtOjF6pjo/view?usp=sharing/)<br>
4. Interface with other system: output the data in csv file and also json file (json is used by other system to udpate location of rider on maps <br>
</ul>


### Flow:
 
Start the app

<br>![GUI](https://github.com/user-attachments/assets/458950ee-d4fd-4c16-a10c-0d8a8c836e5f)
<br> as soon as app starts it will create two file template '
<br>![image](https://github.com/user-attachments/assets/04d8297e-80b8-43cd-a298-09fb20ecedf9)
<br> 'IDN_Mapping.csv' contains 
<br>![IDN_Mapping](https://github.com/user-attachments/assets/f85292de-cbbc-44bb-8704-c598320f93d7)
<br> 'json_include' will determine if rider should be infculed in the json file its like a filter as on maps may be clear the clutter and see only top , lowest rider 
<br> from this app can control the how the rider can be higlighted with yellow color and re color based on the thresold 
<br>![highlight_rider](https://github.com/user-attachments/assets/6ce2c80e-a4b5-4daa-8216-d708cd80871e)
<br> all these can be changed 
<br> next configuration file is 'settings_file.jsonv' contains
<br> ![image](https://github.com/user-attachments/assets/36d3b0af-5c8f-4d07-9cb8-09e768394307)
<br> it makes the setting persistent



<br>you can conifgure the app by going into 'settings' 
<br>![image](https://github.com/user-attachments/assets/8234e6ba-8564-494e-9e41-42f65d0a441a)
<br> top fields are for the TCP interface <br> and bottom filed for the json output which will determine the updatation frequency of the data
<br> As this Json file will update the on maps

#### output:
<br> CSV data out put
<br> ![image](https://github.com/user-attachments/assets/de296d52-e40e-43f2-8f5a-3c37beed82e7)
<br> json data out put
<br> ![output_json](https://github.com/user-attachments/assets/b13b7e33-2316-49a3-8e74-d30ac8a05655)
<br> data will null fileds means it was filer out by 'IDN_Mapping.csv'

##### please do let me know if have any question





