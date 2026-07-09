from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

client = MLClient(
    credential=DefaultAzureCredential(),
    registry_name="azure-huggingface",
)

model_id = "<MODEL_ID>"  # e.g., `Qwen/Qwen3.6-27B`
model = client.models.get(name=model_id.lower().replace("/", "--"), label="latest")
print(model.version)
