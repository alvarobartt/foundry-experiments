---
name: hugging-face-on-foundry
description: Deploy a model from the Hugging Face Hub to Microsoft Foundry on Managed Compute.
---

Deploy a model to Azure AI Foundry using Managed Compute and the `az` CLI.

## When to use

Use this skill when the user asks things like:
- "Can you deploy Qwen3.6-27B-FP8 on Foundry?"
- "Deploy this model on Azure Foundry with Managed Compute"
- "Help me deploy and test a model in Foundry"

Do not use it for Serverless API deployments, as those fall under a different category.

## Prerequisites

- An Azure subscription with access to Microsoft Foundry
- A Microsoft Foundry resource
- `az` CLI installed and be logged in with `az login`
- Python 3.10 or higher installed
- `pip install azure-identity azure-ai-ml azure-mgmt-cognitiveservices openai`
- `azure-ai-ml` needs to be 1.34.0 or greater

It's recommended when applicable to use `uv` and an environment. So unless there's already an active environment in `.venv`, then create it as `uv venv --python 3.11` and activate it as `source .venv/bin/activate` for Bash.

## Step-by-step

### 1. Validate

The user should've provided a model ID from the Hugging Face Hub, which you will need to either complete or verify.

The model ID might've been provided as `Qwen3.6-27B`, which is not correct, since it's missing the author information, in this case being `Qwen`, so the complete model ID is `Qwen/Qwen3.6-27B`. For that, you should use the `hf` CLI to search for whatever the user prompts as `hf models list --search "Qwen3.6 27B" --sort downloads --format json --limit 10` and then get the value of those results by `id` to see which one is the user referring too. Additionally, you can as well run the same query but sorting by trendiness as `hf models list --search "Qwen3.6 27B" --sort trending_score --format json --limit 10`.

If the model is indeed provided completely as `Qwen/Qwen3.6-27B`, you still need to verify that's a public and non-gated model that's available on the Hugging Face Hub with `hf models info Qwen/Qwen3.6-27B`, which can either return the JSON with the model information or rather an error like "Error: Model '...' not found.". Note that if the JSON has been returned, you will need to ensure that `private: false` and `gated: false`.

### 2. Find

After the model is validated, you should also check that the model exists on Microsoft Foundry, so for that you need to use the `references/foundry-model.py` so that given the Hugging Face Hub model ID, you run it to check whether the model is available, and if so, which is it's latest version. If not available, consider the model not deployable for the moment, as they will need to reach out to Hugging Face to onboard that model.

Assuming that the provided model was clear enough and is available on the Hugging Face catalog on Microsoft Foundry i.e., the `azure-huggingface` registry, then you need to run `references/foundry-deployment-templates.py` to get the latest version of the current model, as well as the deployment-templates it supports and their information such as the `acceleratorType` and the `description`, to help the user take a decision later on.

Note that as the capacity for Microsoft Foundry is using a global managed quota, it's a bit different and there's no API yet to fetch that information, so let's assume that the capacity is the one mentioned above.

### 3. Deploy

Then with the model and the deployment-template URIs you need to select one deployment-template to use, which can come in multiple flavours depending on the capabilities as e.g,. context-length, or the instance/s it uses.

Note that the only available `acceleratorType` values as of today are A100_80GB, H100_80GB, and MI300_192GB, and their cost is $3.95, $7.91, and $7.91, per accelerator, respectively, so a deployment-template that requires 4 accelerators, its cost will be 4 times that per hour.

Given that running those costs money, you should ask the user which one of the different alternatives they want to deploy, including the trade-off between those if any, otherwise simply mention the difference on the price, unless there's something in each deployment-template description that's relevant for the user to know.

If they rather prefer you to go ahead without asking them, then use whichever is the default deployment-template, and if it is either CPU or NVIDIA T4 i.e., not supported on Microsoft Foundry, then out of the existing deployment-templates use the cheapest or most efficient in the following order: A100_80GB, MI300_192GB, and H100_80GB.

Once they decide, then simply run `reference/foundry-deploy.py` with the actual replacements and wait until the endpoint is running on Microsoft Foundry.

### 4. Use

Once deployed, you will be able to use it i.e., send HTTP requests to it. As it's deployed under a router on Microsoft Foundry, you need to send OpenAI-compatible requests to e.g., Chat Completions API via an endpoint that looks like `https://<ACCOUNT_NAME>.services.ai.azure.com/openai/v1`. Then you have `references/foundry-primary-key.py` on how to obtain the primary key to be used to send requests to the endpoint. Note that for chat-completion models that usually means either `/v1/chat/completions` or `/v1/responses` (for reasoning models).

```bash
curl https://<ACCOUNT_NAME>.services.ai.azure.com/openai/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $AZURE_API_KEY" \
    -d '{"model":"<DEPLOYMENT_NAME>","messages":[{"role":"user","content":"How does Hugging Face make money?"}],"stream":true}'
```

Alternatively, you can also run `references/foundry-chat.py` for the chat completions models to send requests to the Chat Completions API via the OpenAI SDK, but note that you can also use the Responses API if the model supports reasoning, since it's better supported with Responses API.

## Troubleshooting

As all the models in the `azure-huggingface` catalog go through an extensive testing process those shouldn't fail on deployment time, but if those fail on inference time make sure to report those. If otherwise, those do fail on deployment time, note that the issue might come due to provisioning or allocating the instances.
