# HomeEnergyConsumptionTracker
This repository contains an home enrgy consumption tracker. The project contains the following components:
- Energy meter blink detector (hardware)
- Raberry Pi program for consuming signals from the energy meter blink detector
- RESTful web-service build with bottle.
- Sensor simulators


The idea behind this projekt is a low cost real time consumption tracker for private homes. The only hardware requiered is a few low cost components (resistors, transistors, diods, etc.) and a Rasberry Pi. The webservice could run on the rasberry pi if you want, but I've used a linux VPS (that I use for other things too...) for that.

The web service api can deliver both current load (based on the latest reported load) and the consumed power for a specified time span.
