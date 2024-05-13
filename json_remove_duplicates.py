import json


def remove_duplicates(input_file, output_file):
    unique_jsons = []

    with open(input_file, "r") as file:
        data = json.load(file)
        for json_object in data:
            if json_object not in unique_jsons:
                unique_jsons.append(json_object)
            else:
                print(json_object)

    with open(output_file, "w") as file:
        json.dump(unique_jsons, file, indent=4)


input_file = "level_2/infosec_meta.json"
output_file = "level_2/infosec_meta.json"
remove_duplicates(input_file, output_file)
