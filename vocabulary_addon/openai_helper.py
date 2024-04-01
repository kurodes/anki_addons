from aqt import mw
import requests
import json

from .constants import *

def get_completion(messages):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        },
        data=json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": messages,
        }),
    )
    if response.status_code != 200:
        err = f"{response.status_code} {response.reason} {response.text}"
        print(err)
        return err
    data = response.json()
    return data['choices'][0]['message']['content']

def gpt_compose_story(words):
    prompt = f"""
Compose an intriguing and fluent short story, tailored for a student with a vocabulary of around 6000 English words.
The story should seamlessly incorporates all the keywords that are delimited by triple backticks.
The story should clearly illustrate the meaning of the keywords.
Do not use any special punctuation to highlight these keywords in your responce.
```
{', '.join(words)}
```
"""
# The story should be drawn from or inspired by books and literature.
# keep the story as short as possible
    messages = [{"role": "user", "content": prompt}]
    # respond = get_completion(messages)
    respond = """
Be careful not to directly call any Qt/UI routines inside the background operation!
If you need to modify the UI after an operation completes (eg show a tooltip), you should do it from the success function.
If the operation needs data from the UI (eg a combo box value), that data should be gathered prior to executing the operation.
If you need to update the UI during the background operation (eg to update the text of the progress window), your operation needs to perform that update on the main thread. For example, in a loop:
"""
    return respond

