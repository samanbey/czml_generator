# CZML Generator
A QGIS plugin for creating CZML files

## Setup
- (If downloaded the latest version from GitHub: Copy the downloaded folder to your QGIS Python plugin folder (typically {your user folder}/.qgis2/python/plugins). `sampleData` and `sampleViewer` folders are not needed there. )
- (Re-)start QGIS
- In QGIS, go to Plugin Manager (remember to check "Show also experimental plugins"), find CZML Generator and enable it.
- The `CZML Generator` menu appears in the Web menu

## Sample data
You can find some sample data to start with in the folder `sampleData`

## Sample viewer
There is a sample Cesium viewer in `sampleViewer` folder. 
- Copy it to your webserver
- Open the chart.html file in a text editor
- If you have a Bing key, insert it at the appropriate place
- Change the CZML data file name and the legend file name where indicated in the code
- Load the document in a browser

## Functions

### Prism Map and Prism Map with time
Use this function to create prism maps with or without temporal animation based on any polygon layers currently opened in QGIS
![Prism map sample image](/images/3Dprism.jpg)

### Scaled models with time
Animated visualization of attribute change in time by placing 3D models whose sizes change with the corresponding attribute value.
![Scaled models sample image](/images/scaledModels.jpg)

### Raised connector lines
Creates raised connector arcs from a line layer. Useful for visualizing connections between a set of points
![Connector lines sample image](/images/connLines.jpg)

### 3D Pie chart
Creates 3D Pie charts at feature centroids
![3D pie charts sample image](/images/piecharts.jpg)

## How to cite
Gede, M.: Using Cesium for 3D Thematic Visualisations on the Web, Proc. Int. Cartogr. Assoc., 1, 45, https://doi.org/10.5194/ica-proc-1-45-2018, 2018. 
