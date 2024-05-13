import streamlit as st
import requests


@st.cache_data
def get_available_options(attr):
    attribute_url = f"http://67.207.73.27/GetInformation?attribute={attr}"
    response = requests.get(attribute_url)
    if response.status_code == 200:
        data = response.json()
        # print(f"Got {attr}")
        return data["data"]
    else:
        return get_available_options(attr)


@st.cache_data
def get_result(request):
    try:
        print("requesting")
        res_url = "http://67.207.73.27/get_courses"
        response = requests.post(res_url, json=request)
        print("requested")
        print(response)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            return response_data
    except Exception as e:
        print(e)
        return []


# Get the following from the api endpoint
provider_list = [None, "youtube"] + get_available_options("provider")
level_list = [None] + get_available_options("level")
language_list = [None] + get_available_options("languages")
pricing_list = get_available_options("cost")
duration_list = [None] + get_available_options("duration")
pace_list = [0] + get_available_options("workload")
certification_cost_list = get_available_options("certification_pricing")

st.title("MOOC Fetcher")
request_to_go = {}

query = st.text_input("Enter Course Details")
request_to_go["query"] = query

provider = st.multiselect("Provider", provider_list)
if None not in provider:
    request_to_go["providers"] = provider

level = st.multiselect("Level", level_list)
if None not in level:
    request_to_go["levels"] = level

cx1, cx2 = st.columns(2)
with cx1:
    languages = st.multiselect("Select Language of course", language_list)
    if None not in languages:
        request_to_go["languages"] = languages
with cx2:
    pricing = st.slider(
        "Select Maximum Price of Course", min(pricing_list), max(pricing_list)
    )
    request_to_go["max_course_price"] = pricing

cxx1, cxx2 = st.columns(2)
with cxx1:
    duration = st.selectbox("Select Duration in Weeks", duration_list)
    if duration is not None:
        request_to_go["max_duration"] = duration
with cxx2:
    pace = st.slider(
        "Select Maximum Pace in Hours/Week", min(pace_list), max(pace_list)
    )
    if pace != 0:
        request_to_go["max_pace"] = pace

cxxx1, cxxx2 = st.columns(2)
with cxxx1:
    certification_needed = st.selectbox("Certification Available", [None, "Yes"])
    if certification_needed is not None:
        request_to_go["certification_needed"] = True
with cxxx2:
    certification_price = st.slider(
        "Select Maximum Cost For Certification",
        min(certification_cost_list),
        max(certification_cost_list),
    )
    request_to_go["certification_pricing_max"] = certification_price


def create_course_elemet(current_result, key):
    if current_result["type"] == "course":
        print(current_result)
        with st.container():
            if "name" in current_result:
                st.header("Course : " + current_result["name"])
            cxx1, cxx2 = st.columns(2)
            with cxx1:
                if "provider" in current_result:
                    st.subheader("Provider : " + current_result["provider"])
            with cxx2:
                if "level" in current_result and current_result["level"] is not None:
                    st.subheader("Level : " + current_result["level"])
            if "cost" in current_result:
                st.write("Course Price", str(current_result["cost"]) + "$")
            cxxxx1, cxxxx2 = st.columns(2)
            with cxxxx1:
                if "duration" in current_result:
                    st.write("Duration: ", str(current_result["duration"]) + " Weeks")
            with cxxxx2:
                if (
                    "workload" in current_result
                    and current_result["workload"] is not None
                ):
                    st.write(
                        "Pace: ", str(current_result["workload"]) + " Hours Per Week"
                    )
            cxxx1, cxxx2 = st.columns(2)
            with cxxx1:
                if "certification" in current_result:
                    st.markdown(
                        f'<p style = "color:{"green" if current_result["""certification"""] == "available" else "red"}"> Certification : {"available" if current_result["certification"] == "available" else "not available"}</p>',
                        unsafe_allow_html=True,
                    )
            with cxxx2:
                if "certification_pricing" in current_result:
                    st.markdown(
                        f'<p> certificate pricing : {current_result["certification_pricing"]}$</p>',
                        unsafe_allow_html=True,
                    )
            cx1, cx2 = st.columns(2)
            with cx1:
                if (
                    "languages" in current_result
                    and current_result["languages"] is not None
                ):
                    st.selectbox(
                        "languages available",
                        current_result["languages"],
                        key=f"{str(key)}lang",
                    )
            with cx2:
                if (
                    "subtitles" in current_result
                    and current_result["subtitles"] is not None
                ):
                    st.selectbox(
                        "subtitles available",
                        current_result["subtitles"],
                        key=f"{str(key)}sub",
                    )
            if "link" in current_result:
                st.link_button("Go to Course", current_result["link"])
    elif current_result["type"] == "youtube":
        with st.container():
            st.header("Course : " + current_result["title"])
            st.subheader("Provider : YouTube")
            st.link_button("Go to Course", current_result["link"])


result_view = st.container()


if st.button("Search For MOOCs"):
    # For youtube
    if "providers" not in request_to_go or "youtube" in request_to_go["providers"]:
        request_to_go["youtube"] = True
        request_to_go["youtube_qty"] = 10
        request_to_go["return_quantity"] = 30
    else:
        request_to_go["youtube"] = False
        request_to_go["youtube_qty"] = 0
        request_to_go["return_quantity"] = 40

    print(request_to_go)
    results = get_result(request_to_go)
    # print(results)

    with result_view:
        st.header("Search Results")
        st.markdown("---")
        for i in range(len(results)):
            create_course_elemet(results[i], i)
            st.markdown("---")
