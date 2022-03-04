# Celestial Buoy Evaluation

This repository contains the _Buoy_ example application we use to evaluate Celestial.
Check out the [main repository](https://github.com/OpenFogStack/celestial) to learn more about Celestial!

## Application

There are three types of components that make up this distributed application.

### Sensor Buoys

The sensor buoys are the data source for the application.
Sensors located on the sea send data and imagery to the application.
The locations of these sensors is based on [real NOAA stations](https://www.ndbc.noaa.gov/data/stations/station_table.txt).
See `stations.csv` for the full list of locations.

### Processors

The processors process the data from sensors.
This can happen in a ground station computers or in the LEO edge.

NOAA Dart processing location:
Pacific Tsunami Warning Center
Building 176
1845 Wasp Boulevard
21.366315122964277, -157.96262184972477

### Data Sinks

Processed data generates events that are read by the data sinks.
These can be island ground stations, e.g., for tsunami warnings, or ships, e.g., for weather warnings.
Ground station locations are located in the `groundstations.csv` file and based on real locations.

Vessel locations from [MarineTraffic](https://www.marinetraffic.com/en/ais/home).
Pacific island locations from [United Nations Environment Programme Island Directory](http://islands.unep.ch/isldir.htm).

## Iridium (NEXT) Constellation

DART buoys use the Iridium constellation for communication.
The current Iridium constellation has six planes of eleven satellites each.
There are spaced along a 180 degree arc (i.e., only ascending above one half of the globe, descending above the other).
They have a 780km altitude and 90 degree inclination (polar orbit).

Iridium offers different "plans" for subscribers, from a few bps bandwidth up to 704Kbps receive (352Kbps transmit, [Certus 700 product](https://www.iridium.com/services/iridium-certus-700/)).
Iridium recommends their [Certus 100 product](https://www.iridium.com/services/iridium-certus-100/) for "vehicles, vessels, and aircraft all over the world" as well as "portable operations like workforce communications, remote monitoring, and real-time asset control".
Certus 100 is capable of 88Kbps TX/RX, so we use that for our clients.

ISLs in NEXT are in the 22.18-22.38 GHz band (Ka band), with 21.6MHz necessary bandwidth for each transponder according to p.16 of [this FCC filing](https://fcc.report/IBFS/SAT-MOD-20131227-00148/1031348.pdf).
I have no idea what that means for data rate.
