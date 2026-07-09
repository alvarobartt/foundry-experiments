from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

mgmt = CognitiveServicesManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="<SUBSCRIPTION_ID>",
)
api_key = mgmt.accounts.list_keys(
    resource_group_name="<RESOURCE_GROUP>", account_name="<ACCOUNT_NAME>"
).key1
