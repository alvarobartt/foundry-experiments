from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

client = CognitiveServicesManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="<SUBSCRIPTION_ID>",
)

deployment = client.managed_compute_deployments.begin_create_or_update(  # type: ignore
    resource_group_name="<RESOURCE_GROUP>",
    account_name="<ACCOUNT_NAME>",
    # NOTE: `deployment_name` can only include alphanumeric characters, underscores
    # and hyphens, and be in between 2 to 64 characters.
    deployment_name="<DEPLOYMENT_NAME>",
    resource={
        "sku": {"name": "GlobalManagedCompute", "capacity": 1},
        "properties": {
            "model": "<MODEL_URI>",
            "deploymentTemplate": "<DEPLOYMENT_TEMPLATE_URI>",
            "acceleratorType": "<ACCELERATOR_TYPE>",
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
        },
    },
).result()
