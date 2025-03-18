# LLM Provider Configuration

This guide explains how to configure the LLM providers for the application.

## Environment Variables

The application uses several environment variables to configure the LLM providers:

### Main Provider Selection
- `LLM_PROVIDER`: The LLM provider to use. Valid values are `ollama` or `openai`. Default is `ollama`.

### Reasoning Model Settings
- `REASONING_MODEL_PATH`: The path to the reasoning model API. 
  - Default for Ollama: `http://192.168.100.231:11434`
  - For OpenAI: Use your OpenAI API endpoint
- `REASONING_MODEL_NAME`: The name of the reasoning model.
  - Default for Ollama: `qwen2.5-coder:32b`
  - For OpenAI: Use your preferred OpenAI model name

### Code Generation Model Settings
- `CODE_MODEL_PATH`: The path to the code generation model API.
  - Default: `http://192.168.100.202:8000/v1`
- `CODE_MODEL_NAME`: The name of the code generation model.
  - Default: `afsim-3b-bf16`

## Examples

### Using Ollama (Default)
```
export LLM_PROVIDER=ollama
export REASONING_MODEL_PATH=http://192.168.100.231:11434
export REASONING_MODEL_NAME=qwen2.5-coder:32b
export CODE_MODEL_PATH=http://192.168.100.202:8000/v1
export CODE_MODEL_NAME=afsim-3b-bf16
```

### Using OpenAI
```
export LLM_PROVIDER=openai
export REASONING_MODEL_PATH=https://api.openai.com/v1
export REASONING_MODEL_NAME=gpt-4o
export CODE_MODEL_PATH=https://api.openai.com/v1
export CODE_MODEL_NAME=gpt-4-1106-preview
export OPENAI_API_KEY=your_api_key_here
```

## Architecture

The application now uses a decoupled architecture where the logic for making calls to LLM providers is abstracted in the `llm_provider.py` module. The existing `ollama_api.py` and `vllm_api.py` modules now import and use the functions from the provider module.

This architecture allows for easy switching between different LLM providers without changing the application code.

## Adding a New Provider

To add a new provider:

1. Modify the `llm_provider.py` file to add a new provider option to the LLM_PROVIDER environment variable.
2. Implement the provider-specific logic in the `make_reasoning_call` and `make_code_gen_call` functions.
3. Update the README to include information about the new provider. 