from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from openai import OpenAI

mgmt = CognitiveServicesManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="<SUBSCRIPTION_ID>",
)
api_key = mgmt.accounts.list_keys(
    resource_group_name="<RESOURCE_GROUP>", account_name="<ACCOUNT_NAME>"
).key1

client = OpenAI(
    base_url="https://<ACCOUNT_NAME>.services.ai.azure.com/openai/v1",
    api_key=api_key,
)

response = client.chat.completions.create(
    model="<DEPLOYMENT_NAME>",
    messages=[{"role": "user", "content": "How does Hugging Face make money?"}],
)
print(response.choices[0].message.content)
