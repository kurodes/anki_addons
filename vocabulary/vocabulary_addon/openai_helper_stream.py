from aqt import mw
import requests
import json
from time import sleep

def get_completion_stream(messages):
    openai_api_key = mw.addonManager.getConfig(__name__)['OPENAI_API_KEY']
    model_name = "gpt-3.5-turbo"
    if mw.addonManager.getConfig(__name__)['ENABLE_GPT_4'] == 4:
        model_name = "gpt-4"
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
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
            # prevent splitting word
            if ' ' in buffer:
                pos = buffer.rindex(' ')
                ret, buffer = buffer[:pos+1], buffer[pos+1:]
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
Wrap the keywords in your responce with single asterisk.
```
{', '.join(words)}
```
"""
# Do not use any special punctuation to highlight these keywords in your responce.
# The story should be drawn from or inspired by books and literature.
# keep the story as short as possible
    messages = [{"role": "user", "content": prompt}]
    respond = get_completion_stream(messages)
    # respond = dummy_stream()
    return respond

def gpt_explain_vocabulary(vocabulary):
    prompt = f"""
作为一个英语单词学习专家，你的任务是帮助我深入地学习和记忆英文单词。我想要学习的单词是{vocabulary}，你需要以以下格式指导我：

单词：（我给出的单词）[单词的美式发音]
词族：单词的所有变体
意思：解释这个单词的常见意思，包括任何重要的同义词或反义词。
例句：提供至少两个使用这个单词的例句和翻译，尽可能选择不同的语境来帮助我理解它的多种用法。
记忆：根据这个单词的含义、拼写、音标等，给出一些创新的记忆技巧，例如联想法、故事法、词根词缀法等。

记住，你的目标是帮助我不仅记住这个单词，而且理解其在实际语境中的应用。
"""
    message = [{"role": "user", "content": prompt}]
    respond = get_completion_stream(message)
    # respond = dummy_stream()
    return respond 
