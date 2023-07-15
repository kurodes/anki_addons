from aqt import mw
import requests
import json
from time import sleep

def get_completion_stream(messages):
    openai_api_key = mw.addonManager.getConfig(__name__)['OPENAI_API_KEY']
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        },
        data=json.dumps({
            "model": "gpt-3.5-turbo",
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
Compose an intriguing and fluent short story, tailored for a student with a vocabulary of around 6000 English words.
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

