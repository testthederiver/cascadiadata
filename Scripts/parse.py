# %%
import pandas as pd
import os 
import json

# %%
data_path = "Data"
file = "wpforms-305-Add-Yourself-to-the-Map-8211-Kumu-People-2023-10-03-19-02-40.xlsx"
file = "wpforms-967-Add-Yourself-to-the-Map-8211-Kumu-People-8211-Multi-Step-2023-10-03-20-45-39.xlsx"
# %%
persons = pd.read_excel(os.path.join(data_path, file))
persons["type"] = "Person"
persons.fillna("")
# %%

wp_to_kumu = {"id": "Hidden Field",
"label": "Full Name",
"email": "Email",
"area": "Are you in, or close enough to one of the areas to attend or organize where the activation tour is heading through?",
"bio": "Short Bio",
"stateorprov": "State or Province",
"city_wa": "City (Washington)",
"city_or": "City (Oregon)",
"city_BC": "City (British Columbia)",
"where": "Where?",
"interests": "Interests / Categories",
"work": "About the work I do",
"website": "Website",
"linkedin": "Linkedin",
"statement": "Why do you feel like your work or bioregionalism is important for the future of the Cascadia Bioregion? (optional)",
"Image": "Profile Picture",
"type": "type"}

wp_to_kumu = {v:k for k,v in wp_to_kumu.items()}


def process_json(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    local_dir = ""
    request_json = request.to_dict()
    request_json = {wp_to_kumu[k]:v for k,v in request_json.items() if k in wp_to_kumu.keys()}
    
    for k,v in request_json.items():
        if pd.isna(v):
            request_json[k] = ""

    json_path = os.path.join(local_dir, "data.json")

    with open(json_path,'r') as fp:
        json_data = json.load(fp)

    ids = []
    for e in json_data["elements"]:
        ids.append(e["id"])

    if request_json["id"] not in ids:
        json_data["elements"].append(request_json)

        stateorprov = request_json["stateorprov"]

        print(stateorprov)
        
        city = ""
        for k in request_json.keys():
            if k.startswith("city_"):
                if not k == "city_to_region":
                    if not pd.isna(request_json[k]):
                        print(request_json[k])
                        city += request_json[k]
        
        short_stateorprov = stateorprov.lower().replace(" ", "")
        stateorprov_id = f"place_stateprov_{short_stateorprov}"

        short_city = city.lower().replace(" ", "")
        city = f"{city}, {stateorprov}"
        city_id = f"place_city_{short_stateorprov}_{short_city}"

        new_city = True
        for entry in json_data["elements"]:
            print(entry)
            if entry["id"] == city_id:
                new_city = False
        
        if new_city:
            json_data["elements"].append({"id": city_id, "label": city, "type": "Place"})
            con = {"id":city, "from":city_id, "to":stateorprov_id, "type": "Location"}
            json_data["connections"].append(con)

        
        place_id = str(hash(request_json["id"]))

        if request_json["type"] == "Organization":
            conn_type = "Organization To Place"
        else:
            conn_type = "Location"

        con = {"id":place_id, "from":request_json["id"], "to":city_id, "type": conn_type}
        json_data["connections"].append(con)
            
        with open(json_path, 'w') as fp:
            json.dump(json_data, fp, indent=2)

for i, e in persons.iterrows():
    process_json(e)
    

# %%
