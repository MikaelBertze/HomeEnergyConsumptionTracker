# HomeEnergyConsumptionTracker
This repository contains an home enrgy consumption tracker. The project contains the following components:
- Energy meter blink detector (hardware)
- Raberry Pi program for consuming signals from the energy meter blink detector
- RESTful web-service build with bottle.
- Sensor simulators


The idea behind this projekt is a low cost real time consumption tracker for private homes. The only hardware requiered is a few low cost components (resistors, transistors, diods, etc.) and a Rasberry Pi. The webservice could run on the rasberry pi if you want, but I've used a linux VPS (that I use for other things too...) for that.

Not only enrgy consumption can be tracked. The database can handle any sensor that outputs a discrete scalar value. In this project, two types of sensors have been implemented. Implementing a new sensor would in most cases only be a few lines of code.

##### Electricity Tick Sensor hardware
The electricity tick sensor is a led blink detector with conversion to current load. The electricity meeter installed by the power company will blink with a diod (IR) 1000 times per consumed kWh. The number of blinks per kWh may varry, but is usually printed on the meter.

For this project, a simple detector was built:
[schema]

##### Ananlog Electricity Meeter Sensor hardware
My house got an old analog meter connected to the heating system. This meter require a different type of sensor that detects a black section on a spinning metal disk. The black mark is marked on the outside of a approximately 2 mm thick disk with a diameter of ~ 15cm. The meter will spin the disk 120 laps per consumed kWh.

A light source is aimed at the disk such that a reflection is created that hits the sensor. The black mark will break the reflection, which is detected by the sensor. 


##### Temperature Sensor
A DS18B20 sensor connected to the rasberry Pi GPIO. 

