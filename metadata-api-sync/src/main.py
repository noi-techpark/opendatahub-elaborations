'''
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
'''
from datetime import datetime, timezone
import os
from urllib.parse import parse_qsl, urlparse
from dotenv import load_dotenv, set_key
import requests

load_dotenv()

CONTENT_API_URL = os.getenv("CONTENT_API_URL")
AUTH_BASE = os.getenv("AUTH_BASE")
REALM = os.getenv("REALM")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# check if a datset has been updated since the last time the script was executed
def isUpdated(url):

  params = {
     "fields": "_Meta.LastUpdate",
     "pagenumber": 1,
     "pagesize":1,
     "rawsort" : "-LastChange"
     }
  
  response = requests.get(url, params)

  if response.status_code == 200:
      
      data = response.json()
      
      if isinstance(data, list):
        items = data
      else:
          items = data.get('Items', [])
      
      if items:
        # Check the last time the dataset was updated
        last_update = items[0].get("_Meta.LastUpdate")
        if(last_update):
          last_update = last_update[:19]
          last_update = datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S')

          # check the last time the script was run and compare
          last_sync = os.getenv("LAST_SYNC_DATE")
          if(last_sync):
            last_sync = datetime.fromisoformat(last_sync)
            return last_sync < last_update
  return True
    
# Updates the timestamp variable that states when the script was last executed
def updateLastSync():
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    set_key(".env", "LAST_SYNC_DATE", timestamp)
    print(f"Updated LAST_SYNC_DATE to {timestamp}")

# Returns a list of all ids of the datasets in the Metadata API
def getAllDatasetIds():
  datasets = []
  pagenumber = 1
  url = f"{CONTENT_API_URL}MetaData"

  while True:

    params = {
    "fields" : "Id",
    "pagenumber" : pagenumber,
    "pagesize": 100
    }

    response = requests.get(url, params=params)

    if(response.status_code == 200):
      data = response.json()
      items = data.get("Items", [])

      for item in items:
            
        datasets.append(item.get("Id"))

      if(not data.get("NextPage")):
        break
      
      pagenumber += 1

    else:
      print("Was not able to get metadata")

  return datasets

# Get the url to the dataset itself, starting from its ID
def getDatasetUrl(id):
  url = f"{CONTENT_API_URL}MetaData/{id}"
  params = {
    "fields" : "ApiUrl"
  }
  response = requests.get(url, params=params)
  if(response.status_code == 200):
    data = response.json()
    return data.get("ApiUrl")

# Returns information about the current dataset, if it has been modified since the last time the script was run
def getDatasetInfo(datasetId):

  dataProviders = set()
  dataLicenses = set()
  record_count = 0
  distinct_base = f"{CONTENT_API_URL}Distinct"

  # Prepare the request
  original_api_url = getDatasetUrl(datasetId)
  parsed = urlparse(original_api_url)
  category = parsed.path.split('/')[-1].lower()
  
  query_params = parse_qsl(parsed.query)
  query_params.extend([
      ("type", category),
      ("fields", "Source"),
      ("fields", "LicenseInfo"),
  ])

  #check if the dataset has any updates
  if not isUpdated(original_api_url):
    print(f"No changes for {original_api_url}, skipping.")
    return None

  response = requests.get(distinct_base, params=query_params)

  print(f"\n--- Dataset: {category} ---")
  print(f"Requesting URL: {response.url}")

  if response.status_code == 200:
      
    items = response.json()

    for item in items:

      # Gather Sources (data providers)
      src = item.get("Source") or "Unknown"
      if isinstance(src, list):
        for s in src: 
          dataProviders.add(str(s))
      else:
          dataProviders.add(str(src))
      
      license = item.get("LicenseInfo.License")

      # Gather licenses
      if license:
        dataLicenses.add(license)
  else:
      print(f"Error: Could not fetch data (Status: {response.status_code})")
      return None
      

  # Get the record count
  record_count = getDatasetRecordCount(original_api_url)

  print(f"Providers: {list(dataProviders)}")
  print(f"Licenses: {list(dataLicenses)}")
  print(f"Record Count: {record_count}")
  
  return {
    "data_providers": list(dataProviders),
    "data_licenses": list(dataLicenses),
    "record_count": record_count
  }

# Get the record count from a specific api url
def getDatasetRecordCount(api_url):
  record_count = 0

  params = [
    ("fields", "Id"),
    ("pagesize", 1),
    ("pagenumber", 1)
  ]

  response = requests.get(api_url, params=params)

  if response.status_code == 200:
    data = response.json()
    
    if isinstance(data, dict):
      return data.get("TotalResults", 0)
    elif isinstance(data, list):
      return len(data)
    
  else:
    print(f"Error: {response.status_code}")

  print(f'URL: {api_url}: {record_count} records')
  return record_count

# Get the access token
def get_access_token():
    token_url = f"{AUTH_BASE}/auth/realms/{REALM}/protocol/openid-connect/token"
    token_form = {
        "grant_type": "client_credentials", # was "password"
        #"username": AUTH_USERNAME,
        #"password": AUTH_PASSWORD,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    print(f"Attempting login for Client: {token_form['client_id']} (M2M Flow)")

    #if CLIENT_SECRET:
    #    token_form["client_secret"] = CLIENT_SECRET

    resp = requests.post(
        token_url,
        data=token_form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

# Update each dataset in the metadata API with the new record count, sources, licenses
def updateDatasets(dataset_ids):
    # Ensure dataset_ids is a list (even for one ID)
    if isinstance(dataset_ids, str):
      dataset_ids = [dataset_ids]

    access_token = get_access_token()
    
    with requests.Session() as session:
      session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
      })

      for id in dataset_ids:
        url = f"{CONTENT_API_URL}MetaData/{id}"
        
        try:
          resp = session.get(url)
          resp.raise_for_status()
          full_metadata = resp.json()

          new_info = getDatasetInfo(id)

          if not(new_info):
             continue 

          full_metadata.update({
              "Sources": new_info.get("data_providers"),
              "DatasetLicenses": new_info.get("data_licenses"),
              "RecordCount": {"Total": new_info.get("record_count")}
          })
          
          response = session.put(url, json=full_metadata, timeout=30)
          
          if response.status_code in [200, 204]:
              print(f"Successfully updated dataset {id}")
          else:
              print(f"Failed {id}: {response.status_code} - {response.text}")
                  
        except Exception as e:
            print(f"Critical error on dataset {id}: {e}")

def main():
    
  dataset_ids = getAllDatasetIds()

  if dataset_ids:
      updateDatasets(dataset_ids)
      updateLastSync()
      print("Metadata update complete.")
  else:
      print("No new datasets to update since last sync.")

if __name__ == "__main__":
    main()