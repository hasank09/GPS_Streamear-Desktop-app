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

##### Step-1: 
Start the app


