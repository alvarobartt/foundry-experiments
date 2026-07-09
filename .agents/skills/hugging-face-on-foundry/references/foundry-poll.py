from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

client = CognitiveServicesManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="<SUBSCRIPTION_ID>",
)

deployment = client.managed_compute_deployments.get(
    account_name="<ACCOUNT_NAME>",
    resource_group_name="<RESOURCE_GROUP>",
    deployment_name="<DEPLOYMENT_NAME>",
)
data = deployment.as_dict() if hasattr(deployment, "as_dict") else deployment
state = data.get("properties", {}).get("provisioningState")
print(state)
