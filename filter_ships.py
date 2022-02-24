import pandas as pd

if __name__ == "__main__":
    # read ships-full.json as pandas dataframe
    df = pd.read_json("ships-full.json")
    print(df.head())

    # save name, id, lat, and long as csv
    df[["SHIPNAME", "LAT", "LON"]].to_csv("ships.csv", index=True)