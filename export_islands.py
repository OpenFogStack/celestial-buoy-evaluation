from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import time

if __name__ == "__main__":
    # download the list of islands from http://islands.unep.ch/Tiocean.htm
    base = "http://islands.unep.ch/"
    url = "Tiocean.htm"
    r = requests.get(base + url)
    soup = bs(r.content, "html.parser")

    # extract the names of the islands where the ocean is "Pacific"
    # create a list of the names of the islands
    islands = set()
    islands_links = set()
    for i in soup.body.contents:
        if i.text.startswith("Pacific"):
            j = i.next_sibling.next_sibling.next_sibling.contents[0]

            print(j)

            # extract the name of the island
            name = j.text
            link = j["href"].split("#")[0]

            islands.add(name)
            islands_links.add(link)

            print("Found {} - {}".format(name, link))

    # find the longitude and latitude of each island
    # iterate over the links in islands_links
    df = pd.DataFrame(columns=["ISLAND", "LATITUDE", "LONGITUDE"])

    for link in islands_links:
        time.sleep(1)
        print("Processing {}".format(link))
        # pull that data
        r = requests.get(base + link)
        soup = bs(r.content, "html.parser")

        # iterate over the islands
        for i in soup.body.find_all("body"):
            for k in i.contents:
                # print(i)
                # element is a title if it is tag b, has a font tag
                # if i.name == "b":
                #     print("is b: {}".format(i))
                #     if i.contents[0].name == "font":
                #         print("content 0 is font: {}".format(i))
                #         if i.contents[0].contents[0].name == "font":
                #             print("content 0 content 0 is font: {}".format(i))
                # else:
                #     print("is not b: {}".format(i))

                if k.name == "b" and k.contents[0].name == "font" and k.contents[0].contents[0].name == "font":
                    elem_name = k.contents[0].contents[0].text
                    print("found element {}".format(elem_name))

                    if elem_name in islands:
                        # yes we want this!
                        # get the longitude and latitude by iterating siblings of i until we get one that has the "º" in the text
                        longitude = None
                        latitude = None

                        for j in k.next_siblings:
                            if longitude != None and latitude != None:
                                df = df.append({"ISLAND": elem_name, "LATITUDE": latitude, "LONGITUDE": longitude}, ignore_index=True)

                                break

                            if "º" in j.text:
                                # if "N" in j.text or "S" in j.text:
                                if latitude == None:
                                    # this is a latitude
                                    latitude = j.text.replace("º", "").replace("N", "").replace("S", "").replace(" ", "")
                                    latitude = float(latitude) * (-1 if "S" in j.text else 1)
                                # elif "E" in j.text or "W" in j.text:
                                elif latitude != None:
                                    # this is a longitude
                                    longitude = j.text.replace("º", "").replace("E", "").replace("W", "").replace(" ", "")
                                    longitude = float(longitude) * (-1 if "W" in j.text else 1)

                            print("{} - {} - {}".format(elem_name, longitude, latitude))

    # write the name of the islands to a csv file
    df.to_csv("islands.csv", index=False)



