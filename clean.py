import json

with open("unified/unified_1_all_keys.json", "r") as file:
    data = json.load(file)

unique_price_values = set()


def convert_to_weeks(time_input):
    components = time_input.split()
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    for i in range(0, len(components), 2):
        value = int(components[i])
        unit = components[i + 1]
        if unit.startswith("w"):
            weeks += value
        elif unit.startswith("d"):
            days += value
        elif unit.startswith("h"):
            hours += value
        elif unit.startswith("m"):
            minutes += value

    weeks += days / 7 + hours / (7 * 24) + minutes / (7 * 24 * 60)
    return round(weeks)


# pricing can be --
# 1. $78.00
#       - certificate available
# 2. free certificate
#       - certificate available
# 3. free trial available
#       - certificate available
#       - paid certificate available
# 4. free online course
#       - certificate available
#       - paid certificate available
#       - $55.00 certificate available
# 5. free online course (audit)
#       - $349.00 certificate available
#       - paid certificate available
#       - certificate available
# 6. $50.00/month

for i in data:

    if i["duration & workload"] is not None:
        x = i["duration & workload"]
        x = x.split(",")

        while "-" in x[0]:
            index = x[0].index("-")
            x[0] = x[0][: index - 1] + x[0][index + 1 :]

        x[0] = x[0].strip()
        i["duration"] = convert_to_weeks(x[0])

        if len(x) == 2:
            workload = x[1].strip()
            split = workload.split(" ")
            if split[0].isdigit():
                i["workload"] = int(split[0])
            elif "-" in split[0]:
                index = split[0].index("-")
                val = int(split[0][index + 1 :])
                i["workload"] = val
        else:
            i["workload"] = None

    else:
        i["duration"] = None
        i["workload"] = None

    # print(i["duration & workload"],"|", i["duration"], i["workload"])

    del i["duration & workload"]

    pricing = i["pricing"]
    if len(pricing.split(" ")) == 1:  # handles  $78.00
        cost = int(float(pricing[1:].replace(",", "")))
        i["cost"] = cost
        if i["certificate"] is not None:
            x = i["certificate"]
            if "available" in x:
                i["certification"] = "available"
            else:
                i["certification"] = "not available"

            if "$" in x:
                xx = int(float(x.split()[0][1:].replace(",", "")))
                i["certification_pricing"] = xx
            elif "paid" in x:
                i["certification_pricing"] = 0
            else:
                i["certification_pricing"] = 0

        else:
            i["certification"] = "not available"
            i["certification_pricing"] = 0
    else:
        if "free" in pricing:
            i["cost"] = 0
        elif "paid" in pricing:
            i["cost"] = 1
        if i["certificate"] is not None:
            x = i["certificate"]

            if "available" in x:
                i["certification"] = "available"
            else:
                i["certification"] = "not available"

            if "$" in x:
                xx = int(float(x.split()[0][1:].replace(",", "")))
                i["certification_pricing"] = xx
            elif "paid" in i["certificate"]:
                i["certification_pricing"] = 0
            else:
                i["certification_pricing"] = 0
        else:
            i["certification"] = "not available"
            i["certification_pricing"] = None

        del i["pricing"]
        del i["certificate"]


with open("unified/unified_1_clean.json", "w") as file:
    json.dump(data, file, indent=4)
