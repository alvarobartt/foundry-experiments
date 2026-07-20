import requests
from azure.identity import DefaultAzureCredential

token = (
    DefaultAzureCredential().get_token("https://management.azure.com/.default").token
)

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default").token

url = "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/providers/Microsoft.CognitiveServices/managedComputeCapacities?api-version=2026-05-15-preview&offer=MaaP"

response = requests.get(
    url,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
)
response.raise_for_status()
data = response.json()

for item in data.get("value", []):
    name = item["name"]
    props = item["properties"]
    print(name, props["availableAccelerators"])
