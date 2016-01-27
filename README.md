# CZML Generator
A QGIS plugin for creating CZML files

## Setup
- Copy the folder to your QGIS Python plugin folder (on Windows typically C:\Users\{username}\.qgis2\python\plugins). "sampleData" and "sampleViewer" folders are not needed there.
- (Re-)start QGIS
- In QGIS, go to Plugin Manager, find CZML Generator and enable it.

## Sample data
You can find some sample data to start with in the folder "sampleData"

## Sample viewer
There is a sample Cesium viewer in "sampleViewer" folder. 
- Copy it to your webserver
- Open the chart.html file in a text editor
- If you have a Bing key, insert it at the appropriate place
- Change the CZML data file name and the legend file name where indicated in the code
- Load the document in a browser
