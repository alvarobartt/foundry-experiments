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

match len(model.allowed_deployment_templates):  # type: ignore
    case 1:  # type: ignore
        name, version = re.search(
            r"/deploymenttemplates/([^/]+)/versions/([^/]+)$",
            model.default_deployment_template,  # type: ignore
        ).groups()
        deployment_template = client.deployment_templates.get(
            name=name, version=version
        )
        print(deployment_template._to_dict())  # type: ignore
    case _:
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

        for deployment_template in model.allowed_deployment_templates:  # type: ignore
            name = re.search(
                r"/deploymenttemplates/([^/]+)/labels/latest$",
                deployment_template.asset_id,  # type: ignore
            )
            if not name:
                continue

            response = requests.get(
                "https://eastus.api.azureml.ms/genericasset/v2.0/"
                f"subscriptions/{registry['subscriptionId']}/"
                f"resourceGroups/{registry['resourceGroup']}/"
                f"providers/Microsoft.MachineLearningServices/registries/"
                f"{registry_name}/deploymenttemplates"
                f"?api-version=2024-04-01-preview&name={quote(name.group(1), safe='')}",
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            for key in ("value", "items"):
                for item in payload.get(key):
                    print(item)
