import json

# LEVEL 1
# computer_science - 9975
# health - 5157
# business - 9975
# maths - 2730
# humanities - 8067
# engineering - 4515
# science - 4300
# education - 2137
# social_sciences - 3795
# art_and_design - 19980
# data_science - 4530
# personal_development - 5565
# infosec - 2445
# programming - 16500

classroom = 0
course = 0

with open("level_2/infosec_meta.json", "r") as file:
    json_data = json.load(file)

# for i in json_data:
#     if "www.classcentral.com/course" in i["link"]:
#         course += 1
#     elif "www.classcentral.com/classroom" in i["link"]:
#         classroom += 1
# print("videos:", classroom, "courses:", course)

json_length = len(json_data)
print("Length of JSON array:", json_length)
