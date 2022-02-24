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

### Data Sinks

Processed data generates events that are read by the data sinks.
These can be island ground stations, e.g., for tsunami warnings, or ships, e.g., for weather warnings.
Ground station locations are located in the `groundstations.csv` file and based on real locations.

Vessel locations from [MarineTraffic](https://www.marinetraffic.com/en/ais/home).
Pacific island locations from [United Nations Environment Programme Island Directory](http://islands.unep.ch/isldir.htm).
