---
id: genai_config
title: Configuring Generative AI
---

## Configuration

A Generative AI provider can be configured in the global config, which will make the Generative AI features available for use. There are currently 5 native providers available to integrate with Frigate: Ollama, Google Gemini, OpenAI, Azure OpenAI, and OpenRouter.

To use Generative AI, you must define a single provider at the global level of your Frigate configuration. If the provider you choose requires an API key, you may either directly paste it in your configuration, or store it in an environment variable prefixed with `FRIGATE_`.

## Ollama

:::warning

Using Ollama on CPU is not recommended, high inference times make using Generative AI impractical.

:::

[Ollama](https://ollama.com/) allows you to self-host large language models and keep everything running locally. It provides a nice API over [llama.cpp](https://github.com/ggerganov/llama.cpp). It is highly recommended to host this server on a machine with an Nvidia graphics card, or on a Apple silicon Mac for best performance.

Most of the 7b parameter 4-bit vision models will fit inside 8GB of VRAM. There is also a [Docker container](https://hub.docker.com/r/ollama/ollama) available.

Parallel requests also come with some caveats. You will need to set `OLLAMA_NUM_PARALLEL=1` and choose a `OLLAMA_MAX_QUEUE` and `OLLAMA_MAX_LOADED_MODELS` values that are appropriate for your hardware and preferences. See the [Ollama documentation](https://github.com/ollama/ollama/blob/main/docs/faq.md#how-does-ollama-handle-concurrent-requests).

### Supported Models

You must use a vision capable model with Frigate. Current model variants can be found [in their model library](https://ollama.com/library). Note that Frigate will not automatically download the model you specify in your config, Ollama will try to download the model but it may take longer than the timeout, it is recommended to pull the model beforehand by running `ollama pull your_model` on your Ollama server/Docker container. Note that the model specified in Frigate's config must match the downloaded model tag.

:::info

Each model is available in multiple parameter sizes (3b, 4b, 8b, etc.). Larger sizes are more capable of complex tasks and understanding of situations, but requires more memory and computational resources. It is recommended to try multiple models and experiment to see which performs best.

:::

:::tip

If you are trying to use a single model for Frigate and HomeAssistant, it will need to support vision and tools calling. qwen3-VL supports vision and tools simultaneously in Ollama.

:::

The following models are recommended:

| Model             | Notes                                                                |
| ----------------- | -------------------------------------------------------------------- |
| `qwen3-vl`        | Strong visual and situational understanding, higher vram requirement |
| `Intern3.5VL`     | Relatively fast with good vision comprehension                       |
| `gemma3`          | Strong frame-to-frame understanding, slower inference times          |
| `qwen2.5-vl`      | Fast but capable model with good vision comprehension                |

:::note

You should have at least 8 GB of RAM available (or VRAM if running on GPU) to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.

:::

### Configuration

```yaml
genai:
  provider: ollama
  base_url: http://localhost:11434
  model: minicpm-v:8b
  provider_options:  # other Ollama client options can be defined
    keep_alive: -1
    options:
        num_ctx: 8192  # make sure the context matches other services that are using ollama
```

## Google Gemini

Google Gemini has a free tier allowing [15 queries per minute](https://ai.google.dev/pricing) to the API, which is more than sufficient for standard Frigate usage.

### Supported Models

You must use a vision capable model with Frigate. Current model variants can be found [in their documentation](https://ai.google.dev/gemini-api/docs/models/gemini). At the time of writing, this includes `gemini-1.5-pro` and `gemini-1.5-flash`.

### Get API Key

To start using Gemini, you must first get an API key from [Google AI Studio](https://aistudio.google.com).

1. Accept the Terms of Service
2. Click "Get API Key" from the right hand navigation
3. Click "Create API key in new project"
4. Copy the API key for use in your config

### Configuration

```yaml
genai:
  provider: gemini
  api_key: "{FRIGATE_GEMINI_API_KEY}"
  model: gemini-1.5-flash
```

## OpenAI

OpenAI does not have a free tier for their API. With the release of gpt-4o, pricing has been reduced and each generation should cost fractions of a cent if you choose to go this route.

### Supported Models

You must use a vision capable model with Frigate. Current model variants can be found [in their documentation](https://platform.openai.com/docs/models). At the time of writing, this includes `gpt-4o` and `gpt-4-turbo`.

### Get API Key

To start using OpenAI, you must first [create an API key](https://platform.openai.com/api-keys) and [configure billing](https://platform.openai.com/settings/organization/billing/overview).

### Configuration

```yaml
genai:
  provider: openai
  api_key: "{FRIGATE_OPENAI_API_KEY}"
  model: gpt-4o
```

:::note

To use a different OpenAI-compatible API endpoint, set the `OPENAI_BASE_URL` environment variable to your provider's API URL.

:::

## Azure OpenAI

Microsoft offers several vision models through Azure OpenAI. A subscription is required.

### Supported Models

You must use a vision capable model with Frigate. Current model variants can be found [in their documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models). At the time of writing, this includes `gpt-4o` and `gpt-4-turbo`.

### Create Resource and Get API Key

To start using Azure OpenAI, you must first [create a resource](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource). You'll need your API key and resource URL, which must include the `api-version` parameter (see the example below). The model field is not required in your configuration as the model is part of the deployment name you chose when deploying the resource.

### Configuration

```yaml
genai:
  provider: azure_openai
  base_url: https://example-endpoint.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2023-03-15-preview
  api_key: "{FRIGATE_OPENAI_API_KEY}"
```

## OpenRouter

[OpenRouter](https://openrouter.ai/) provides a unified API to access multiple AI providers including OpenAI, Google, Anthropic, Meta, and more. This allows you to easily switch between different models and providers without changing your configuration structure. OpenRouter uses a pay-as-you-go pricing model with competitive rates.

### Supported Models

OpenRouter supports a wide variety of vision-capable models from different providers. Popular options include:

- Google models: `google/gemini-2.0-flash`, `google/gemini-1.5-pro`
- OpenAI models: `openai/gpt-4o`, `openai/gpt-4o-mini`
- Anthropic models: `anthropic/claude-3.5-sonnet`, `anthropic/claude-3-opus`
- Meta models: `meta-llama/llama-3.2-90b-vision-instruct`
- And many more - see the [full model list](https://openrouter.ai/models)

:::tip

When choosing a model, consider both cost and performance. Many models are available, and OpenRouter makes it easy to experiment by simply changing the `model` parameter without modifying your API configuration.

:::

### Get API Key

To start using OpenRouter:

1. Visit [OpenRouter](https://openrouter.ai/) and sign up for an account
2. Navigate to the [API Keys page](https://openrouter.ai/keys)
3. Create a new API key
4. Add credits to your account in the [Credits page](https://openrouter.ai/credits)

### Configuration

```yaml
genai:
  provider: openrouter
  api_key: "{FRIGATE_OPENROUTER_API_KEY}"
  model: google/gemini-2.0-flash
```

:::note

The default base URL for OpenRouter is `https://openrouter.ai/api/v1`, but you can override it by setting the `base_url` parameter in your configuration if needed.

:::
