import json
import logging
import re
from abc import ABC, abstractmethod
from typing import List

import g4f
from google import generativeai as genai
from loguru import logger
from openai import AzureOpenAI, OpenAI, OpenAIError
from openai.types.chat import ChatCompletion

from luoxia.app.config import CONF

llm_generate_max_retries = CONF.default.llm_generate_max_retries


class GetLLMProvide(ABC):

    def __init__(self):
        self.api_version = ""  # for azure
        self.api_key = CONF.default.api_key
        self.model_name = CONF.default.model_name
        self.base_url = CONF.default.base_url
        self.model_name = CONF.default.model_name

    @abstractmethod
    def get_contant(self):
        pass


class QwenLLM(GetLLMProvide):

    def get_contant(self, prompt):
        import dashscope
        from dashscope.api_entities.dashscope_response import GenerationResponse

        dashscope.api_key = self.api_key
        response = dashscope.Generation.call(
            model=self.model_name, messages=[{"role": "user", "content": prompt}],
        )
        if response:
            if isinstance(response, GenerationResponse):
                status_code = response.status_code
                if status_code != 200:
                    raise Exception(f'[qwen] returned an error response: "{response}"')

                content = response["output"]["text"]
                return content.replace("\n", "")
            else:
                raise Exception(f'[qwen] returned an invalid response: "{response}"')
        else:
            raise Exception(f"[qwen] returned an empty response")


class GeminiLLM(GetLLMProvide):

    def get_contant(self, prompt):

        genai.configure(api_key=self.api_key, transport="rest")

        generation_config = {
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        try:
            response = model.generate_content(prompt)
            candidates = response.candidates
            generated_text = candidates[0].content.parts[0].text
        except (AttributeError, IndexError) as e:
            print("Gemini Error:", e)

        return generated_text


class CloudflareLLM(GetLLMProvide):

    def get_contant(self, prompt):
        import requests

        response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{CONF.default.account_id}/ai/run/{self.model_name}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "messages": [
                    {"role": "system", "content": "You are a friendly assistant"},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        result = response.json()
        logger.info(result)
        return result["result"]["response"]


class ErnieLLM(GetLLMProvide):

    def get_contant(self, prompt):
        import requests

        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": CONF.default.secret_key,
        }
        access_token = (
            requests.post("https://aip.baidubce.com/oauth/2.0/token", params=params)
            .json()
            .get("access_token")
        )
        url = f"{self.base_url}?access_token={access_token}"

        payload = json.dumps(
            {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "top_p": 0.8,
                "penalty_score": 1,
                "disable_search": False,
                "enable_citation": False,
                "response_format": "text",
            },
        )
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, headers=headers, data=payload).json()
        return response.get("result")


class AzureLLM(GetLLMProvide):

    def get_contant(self, prompt):
        client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.base_url,
        )
        response = client.chat.completions.create(
            model=self.model_name, messages=[{"role": "user", "content": prompt}],
        )
        if response:
            if isinstance(response, ChatCompletion):
                content = response.choices[0].message.content
            else:
                raise Exception(
                    f'[{CONF.default.llm_provider}] returned an invalid response: "{response}", please check your network '
                    f"connection and try again.",
                )
        else:
            raise Exception(
                f"[{CONF.default.llm_provider}] returned an empty response, please check your network connection and try again.",
            )

        return content.replace("\n", "")


class OtherLLM(GetLLMProvide):

    def get_contant(self, prompt):
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        try:
            response = client.chat.completions.create(
                model=self.model_name, messages=[{"role": "user", "content": prompt}],
            )
        except OpenAIError as e:
            raise Exception(f"{CONF.default.llm_provider} config error, please check it")
        except Exception as e:
            raise Exception(f"[{CONF.default.llm_provider}] connection fail")
        if response:
            if isinstance(response, ChatCompletion):
                content = response.choices[0].message.content
            else:
                raise Exception(
                    f"[{CONF.default.llm_provider}] returned an invalid response: '{response}', "
                    "please check your network connection and try again.",
                )
        else:
            raise Exception(
                f"[{CONF.default.llm_provider}] returned an empty response, please check"
                "your network connection and try again.",
            )

        return content.replace("\n", "")


class G4gLLM(GetLLMProvide):

    def get_contant(self, prompt):

        content = g4f.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )

        return content.replace("\n", "")


def select_llm_provider(llm_provider: str) -> GetLLMProvide:
    match llm_provider:
        case "qwen":
            return QwenLLM()
        case "gemini":
            return GeminiLLM()
        case "cloudflare":
            return ErnieLLM()
        case "ernie":
            return ErnieLLM()
        case "azure":
            return AzureLLM()
        case "g4f":
            return G4gLLM()
        case _:
            return OtherLLM()


def prompt_script(video_subject: str, paragraph_number: str) -> str:
    return f""" 
# Role: Video Script Generator

## Goals:
Generate a script for a video, depending on the subject of the video.

## Constrains:
1. the script is to be returned as a string with the specified number of paragraphs.
2. do not under any circumstance reference this prompt in your response.
3. get straight to the point, don't start with unnecessary things like, "welcome to this video".
4. you must not include any type of markdown or formatting in the script, never use a title.
5. only return the raw content of the script.
6. do not include "voiceover", "narrator" or similar indicators of what should be spoken at the beginning of each paragraph or line.
7. you must not mention the prompt, or anything about the script itself. also, never talk about the amount of paragraphs or lines. just write the script.
8. respond in the same language as the video subject.

# Initialization:
- video subject: {video_subject}
- number of paragraphs: {paragraph_number}
""".strip()


def generate_script(video_subject: str, language: str = "", paragraph_number: int = 1) -> str:
    logger.info(f"llm provider type {CONF.default.llm_provider}")
    prompt = prompt_script(video_subject, paragraph_number)
    if language:
        prompt += f"\n- language: {language}"

    final_script = ""
    logger.info(f"subject: {video_subject}")

    def format_response(response):
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Select the specified number of paragraphs
        selected_paragraphs = paragraphs[:paragraph_number]

        # Join the selected paragraphs into a single string
        return "\n\n".join(paragraphs)

    for i in range(llm_generate_max_retries):
        try:
            response = select_llm_provider(CONF.default.llm_provider).get_contant(prompt=prompt)
            if response:
                final_script = format_response(response)
            else:
                logging.error("gpt returned an empty response")

            # g4f may return an error message
            if final_script and "当日额度已消耗完" in final_script:
                raise ValueError(final_script)

            if final_script:
                break
        except Exception as e:
            logger.error(f"failed to generate script: {e}")

        if i < llm_generate_max_retries:
            logger.warning(f"failed to generate video script, trying again... {i + 1}")

    logger.success(f"completed: \n{final_script}")
    return final_script.strip()


def prompt_terms(amount: str, video_subject: str, video_script: str) -> str:
    return f"""
# Role: Video Search Terms Generator

## Goals:
Generate {amount} search terms for stock videos, depending on the subject of a video.

## Constrains:
1. the search terms are to be returned as a json-array of strings.
2. each search term should consist of 1-3 words, always add the main subject of the video.
3. you must only return the json-array of strings. you must not return anything else. you must not return the script.
4. the search terms must be related to the subject of the video.
5. reply with english search terms only.

## Output Example:
["search term 1", "search term 2", "search term 3","search term 4","search term 5"]

## Context:
### Video Subject
{video_subject}

### Video Script
{video_script}

Please note that you must use English for generating video search terms; Chinese is not accepted.
""".strip()


def generate_terms(video_subject: str, video_script: str, amount: int = 5) -> List[str]:
    prompt = prompt_terms(amount, video_subject, video_script)

    logger.info(f"subject: {video_subject}")

    search_terms = []
    response = ""
    for i in range(llm_generate_max_retries):
        try:
            response = select_llm_provider(CONF.default.llm_provider).get_contant(prompt=prompt)
            search_terms = json.loads(response)
            if not isinstance(search_terms, list) or not all(
                isinstance(term, str) for term in search_terms
            ):
                logger.error("response is not a list of strings.")
                continue

        except Exception as e:
            logger.warning(f"failed to generate video terms: {str(e)}")
            if response:
                match = re.search(r"\[.*]", response)
                if match:
                    try:
                        search_terms = json.loads(match.group())
                    except Exception as e:
                        logger.warning(f"failed to generate video terms: {str(e)}")
                        pass

        if search_terms and len(search_terms) > 0:
            break
        if i < llm_generate_max_retries:
            logger.warning(f"failed to generate video terms, trying again... {i + 1}")

    logger.success(f"completed: \n{search_terms}")
    return search_terms


if __name__ == "__main__":
    video_subject = "生命的意义是什么"
    # script = generate_script(
    #     video_subject=video_subject, language="zh-CN", paragraph_number=1
    # )
    # print("######################")
    # script = "生命的意义常常被视为一个深奥而复杂的问题，不同的人有不同的理解。对于一些人来说，生命的意义可能在于追求幸福和满足，享受生活中的每一个瞬间，珍惜与家人和朋友的关系。另一些人则可能认为，生命的意义在于实现个人目标和理想，通过努力工作和不断学习来提升自己，创造出对社会有益的成就。此外，还有人从宗教或哲学的角度寻找生命的意义，认为人生的目的在于探索精神世界，追求更高的真理和智慧。无论是哪种观点，生命的意义最终都与个人的经历、价值观和信仰密切相关。"
    # search_terms = generate_terms(
    #     video_subject=video_subject, video_script=script, amount=5
    # )
    # print("######################")
    # print(search_terms)
    search_terms = [
        "meaning of life",
        "life purpose",
        "personal growth",
        "happiness journey",
        "self-discovery",
    ]
