import json
import requests
from time import sleep

from aqt import mw

from .constants import *

def get_completion_stream(messages):
    model_name = "gpt-3.5-turbo"
    if ENABLE_GPT_4 == True:
        model_name = "gpt-4"
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        },
        data=json.dumps({
            "model": model_name,
            # "model": "gpt-4",
            "messages": messages,
            "stream": True
        }),
        stream=True
    )

    if response.status_code != 200:
        yield f"{response.status_code} {response.reason} {response.text}"
    else:
        full_response = ""
        buffer = ""
        for line in response.iter_lines():
            if not line:
                continue
            resp_dict = json.loads(line.decode("utf-8")[6:])
            if resp_dict["choices"][0]["finish_reason"] == "stop":
                if buffer:
                    yield buffer
                break
            delta_content = resp_dict["choices"][0]["delta"]["content"]
            full_response += delta_content
            buffer += delta_content
            # prevent splitting inside a word
            if ' ' in buffer:
                pos = buffer.rindex(' ')
                ret, buffer = buffer[:pos + 1], buffer[pos + 1:]
                yield ret


def dummy_stream():
    for i in range(10):
        yield f"line {i}."
        sleep(0.2)


def gpt_compose_story_stream(words):
    prompt = f"""
Compose an intriguing and fluent short story, tailored for a student with a vocabulary of around 5000 English words.
The story should seamlessly incorporates all the keywords that are delimited by triple backticks.
The story should clearly illustrate the meaning of the keywords.
Wrap the keywords in your response with single asterisk.
```
{', '.join(words)}
```
"""
    # Do not use any special punctuation to highlight these keywords in your response.
    # The story should be drawn from or inspired by books and literature.
    # keep the story as short as possible
    messages = [{"role": "user", "content": prompt}]
    respond = get_completion_stream(messages)
    # respond = dummy_stream()
    return respond


def gpt_explain_word_stream(vocabulary):
    prompt = f"""
你是一个英语专家，你的任务是帮助中文母语的学生学习英文单词。你需要一步步地完成下面的步骤，来帮助学生全面的学习{vocabulary}这个单词：
1.单词：单词 [标准的美式发音]
2.含义：列出单词最常见的中文含义
3.例句：为单词的每个含义提供例句及其翻译
4.记忆：根据这个单词的拼写，采用词根词缀法等方法，给出单词的的记忆技巧
5.词族：列出单词的词族，和它们的含义
6.关联：列出单词的近义词、反义词，和它们的含义
"""
    message = [{"role": "user", "content": prompt}]
    respond = get_completion_stream(message)
    # respond = dummy_stream()
    return respond
