import json
import logging
import os
import time
from typing import Any, Dict, List, Union

from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from ollama import Client

# Reasoning model settings
REASONING_MODEL_PATH = os.environ.get(
    'REASONING_MODEL_PATH', 'http://192.168.100.231:11434')
REASONING_MODEL_NAME = os.environ.get(
    'REASONING_MODEL_NAME', "qwen2.5-coder:32b")
REASONING_MODEL_PROVIDER = os.environ.get(
    'REASONING_MODEL_PROVIDER', 'ollama')  # 'ollama' or 'openai'

# Code model settings
CODE_MODEL_PATH = os.environ.get(
    'CODE_MODEL_PATH', 'http://192.168.100.231:11434/v1')  # "http://127.0.0.1:11434"
CODE_MODEL_NAME = os.environ.get('CODE_MODEL_NAME', "afsim-3b")
CODE_MODEL_PROVIDER = os.environ.get('CODE_MODEL_PROVIDER', 'openai')
# CODE_MODEL_PATH = os.environ.get(
#     'CODE_MODEL_PATH', "http://192.168.100.201:8000/v1")
# CODE_MODEL_NAME = os.environ.get('CODE_MODEL_NAME', "afsim-3b-bf16")
# CODE_MODEL_PROVIDER = os.environ.get('CODE_MODEL_PROVIDER', 'openai')

print(f"REASONING_MODEL_PATH: {REASONING_MODEL_PATH}")
print(f"REASONING_MODEL_NAME: {REASONING_MODEL_NAME}")
print(f"REASONING_MODEL_PROVIDER: {REASONING_MODEL_PROVIDER}")
print(f"CODE_MODEL_PATH: {CODE_MODEL_PATH}")
print(f"CODE_MODEL_NAME: {CODE_MODEL_NAME}")
print(f"CODE_MODEL_PROVIDER: {CODE_MODEL_PROVIDER}")

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# TODO: 需要优化，统一不同 API 的调用方式

# Initialize clients based on provider
if REASONING_MODEL_PROVIDER == 'ollama':
    try:
        reasoning_ollama_client = Client(host=REASONING_MODEL_PATH)
    except ImportError:
        logger.error(
            "Ollama package not installed but LLM_PROVIDER is set to 'ollama'")
        reasoning_ollama_client = None
else:
    reasoning_openai_client = ChatOpenAI(
        model=REASONING_MODEL_NAME,
        openai_api_key="EMPTY",
        openai_api_base=REASONING_MODEL_PATH,
        max_tokens=2000,
        temperature=0.2,
    )

code_ollama_client = Client(host=CODE_MODEL_PATH)
# Initialize OpenAI client for code generation
code_openai_client = ChatOpenAI(
    model=CODE_MODEL_NAME,
    openai_api_key="EMPTY",
    openai_api_base=CODE_MODEL_PATH,
    max_tokens=2000,
    temperature=0.2,
)


def make_reasoning_call(messages: List, max_tokens=300, is_final_answer=False) -> Dict[str, Any]:
    """
    Makes a reasoning call to the selected LLM provider.

    Args:
        messages: List of message objects
        max_tokens: Maximum number of tokens to generate
        is_final_answer: Flag indicating if this is a final answer request

    Returns:
        Dictionary containing the response
    """
    logger.info(
        "Starting make_reasoning_call function using provider: " + REASONING_MODEL_PROVIDER)
    logger.info(f"API request: {messages}")

    for attempt in range(3):
        try:
            if REASONING_MODEL_PROVIDER == 'ollama':
                # Ollama implementation
                response = reasoning_ollama_client.chat(
                    REASONING_MODEL_NAME,
                    messages=messages,
                    options={"temperature": 0.2},
                    format='json',
                )
                logger.info(f"API response: {response}")
                return json.loads(response['message']['content'])

            elif REASONING_MODEL_PROVIDER == 'openai':
                # OpenAI implementation
                openai_messages = [
                    {"role": msg["role"], "content": msg["content"]} for msg in messages]

                response = reasoning_openai_client.invoke(openai_messages)
                logger.info(f"API response: {response}")

                # Parse the response content as JSON
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    # If not valid JSON, return as is
                    return {"title": "Response", "content": response.content}

            else:
                error_msg = f"Unsupported LLM provider: {REASONING_MODEL_PROVIDER}"
                logger.error(error_msg)
                return {"title": "Error", "content": error_msg, "next_action": "final_answer"}

        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")

            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

    logger.info("Ending make_reasoning_call function")


def make_code_gen_call(messages: List[BaseMessage]) -> Union[Any, Dict[str, Any]]:
    """
    Makes a code generation call to the selected LLM provider.

    Args:
        messages: List of message objects from LangChain

    Returns:
        Response from the code generation model
    """
    logger.info(
        "Starting make_code_gen_call function using provider: " + CODE_MODEL_PROVIDER)

    for attempt in range(3):
        try:
            if CODE_MODEL_PROVIDER == 'openai':
                # Default OpenAI implementation
                return code_openai_client.invoke(messages)

            elif CODE_MODEL_PROVIDER == 'ollama':
                # Convert LangChain messages to Ollama format
                ollama_messages = []
                for msg in messages:
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        role = "system" if msg.type == "system" else "user"
                        ollama_messages.append(
                            {"role": role, "content": msg.content})

                response = code_ollama_client.chat(
                    CODE_MODEL_NAME,
                    messages=ollama_messages,
                    options={"temperature": 0.2},
                )

                # Return a content object similar to what LangChain would return
                return response['message']

            else:
                error_msg = f"Unsupported LLM provider: {CODE_MODEL_PROVIDER}"
                logger.error(error_msg)
                return {"title": "Error", "content": error_msg}

        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")

            if attempt == 2:
                return {"title": "Error", "content": f"Failed to generate code after 3 attempts. Error: {str(e)}"}
            time.sleep(1)  # Wait for 1 second before retrying
