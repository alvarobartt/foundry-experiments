import json
import re
from urllib.parse import quote

import requests
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
registry_name = "azure-huggingface"
client = MLClient(credential=credential, registry_name=registry_name)

model_id = "<MODEL_ID>"  # e.g., `Qwen/Qwen3.6-27B`
version = "<VERSION>"  # e.g., `1`
model = client.models.get(name=model_id.lower().replace("/", "--"), version=version)
model_dict = model._to_dict()  # type: ignore

template_uris = []
for deployment_template in getattr(model, "allowed_deployment_templates", []) or []:
    if getattr(deployment_template, "asset_id", None):
        template_uris.append(deployment_template.asset_id)

default_template = model_dict.get("default_deployment_template") or {}
if default_template.get("asset_id"):
    template_uris.append(default_template["asset_id"])

template_names = []
for template_uri in template_uris:
    match = re.search(
        r"/deploymenttemplates/([^/]+)/(?:labels/latest|versions/[^/]+)$",
        template_uri,
    )
    if match and match.group(1) not in template_names:
        template_names.append(match.group(1))

if not template_names:
    raise RuntimeError("No deployment templates found for this model.")

token = credential.get_token("https://management.azure.com/.default").token
headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

response = requests.get(
    "https://eastus.api.azureml.ms/registrymanagement/v1.0/"
    f"registries/{registry_name}/discovery",
    headers=headers,
    timeout=60,
)
response.raise_for_status()
registry = response.json()

for template_name in template_names:
    response = requests.get(
        "https://eastus.api.azureml.ms/genericasset/v2.0/"
        f"subscriptions/{registry['subscriptionId']}/"
        f"resourceGroups/{registry['resourceGroup']}/"
        f"providers/Microsoft.MachineLearningServices/registries/"
        f"{registry_name}/deploymenttemplates"
        f"?api-version=2024-04-01-preview&name={quote(template_name, safe='')}",
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    for key in ("value", "items"):
        for item in payload.get(key, []):
            print(json.dumps(item, indent=2))
