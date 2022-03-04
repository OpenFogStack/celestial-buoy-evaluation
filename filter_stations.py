import pandas as pd

if __name__ == "__main__":
    stations = pd.read_csv("stations-full.csv", sep="|")

    print(stations.head())

    # get ID, station name, and location
    stations = stations[["STATION_ID", "NAME", "LOCATION", "OWNER", "TTYPE"]]

    print(stations.head())

    # parse location (format 30.000 N 90.000 W (30&#176;0"0" N 90&#176;0"0" W)) to latitude and longitude

    stations["LATITUDE"] = stations["LOCATION"].apply(lambda x: (1 if x.split(" ")[1] == "N" else -1) * float(x.split(" ")[0]))
    stations["LONGITUDE"] = stations["LOCATION"].apply(lambda x: (1 if x.split(" ")[3] == "E" else -1) * float(x.split(" ")[2]))

    print(stations.head())

    # remove location column
    stations = stations.drop("LOCATION", axis=1)

    print(stations.head())

    # write to csv
    stations.to_csv("stations.csv", index=False)

    print(stations.head())