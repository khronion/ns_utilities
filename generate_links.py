import urllib.request
import xml.etree.cElementTree as et
import time
import math

# Configuration

region = "Kingdom of Alexandria"
user_agent = "Khronion <khronion@gmail.com>"
rate = 40 / 30

# End Configuaration


def fix(s):
    return s.lower().replace(" ", "_")

region_query = "https://www.nationstates.net/cgi-bin/api.cgi?region={}" \
              "&q=delegateauth+nations+officers+founderauth+delegate+delegateauth+delegatevotes+founder"\
              .format(fix(region))

nation_query = "https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=endorsements"

# get list of nations

print("Getting data for region " + region)

region_api_call = urllib.request.Request(url=region_query, headers={'User-Agent': user_agent})
time.sleep(rate)
nation_list = et.fromstring((urllib.request.urlopen(region_api_call).read().decode())).find("NATIONS").text.split(":")

# generate unique ID for every nation

id = {}
i = 0

with open(fix(region) + '.nodes.csv', 'w') as out:
    out.write('id,Label\n')
    for nation in nation_list:
        id[nation] = i
        out.write(str(i) + "," + nation + '\n')
        i += 1


# process nations and generate CSV of all links

with open(fix(region) + ".edges.csv", 'w') as out:
    print("Processing endorsements for " + region)
    out.write("Source,Target\n")

    progress = 0
    for nation in nation_list:
        # query API
        nation_api_call = urllib.request.Request(url=nation_query.format(nation), headers={'User-Agent': user_agent})
        time.sleep(rate)
        try:
            endorsement_list = et.fromstring((urllib.request.urlopen(nation_api_call).read().decode()))\
                .find("ENDORSEMENTS").text.split(",")

            for endorsement in endorsement_list:
                print("\t" + endorsement + " endorsing " + nation)
                out.write(str(id[endorsement]) + ',' + str(id[nation]) + '\n')

        except AttributeError:
            pass  # nation has no endorsements

        progress += 1
        print(str(math.floor(progress / len(nation_list)*100)) + "% complete")

