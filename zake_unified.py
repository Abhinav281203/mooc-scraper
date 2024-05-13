import json


paths = [
    "cs_meta.json",
    "science_meta.json",
    "personal_development_meta.json",
    "health_meta.json",
    "datascience_meta.json",
    "education_meta.json",
    "programming_meta.json",
    "humanities_meta.json",
    "maths_meta.json",
]

paths_1 = ["engineering_meta.json", "business_meta.json"]

output_file = "unified.json"
output_data = []

for path in paths:
    with open(f"level_2/{path}", "r") as input:
        data = json.load(input)
        print(f"{path} - {len(data)}")
        output_data.extend(data)

with open(output_file, "w") as output:
    json.dump(output_data, output, indent=4)
    print(f"output_file - {len(output_data)}")
