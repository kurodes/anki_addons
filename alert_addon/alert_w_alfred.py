import sys
import json
import shlex
import urllib.request
import subprocess as sp

from typing import Tuple

def request(action, **params):
    print(params)
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def shell(cmd: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Executes shell commands as at the Terminal. Consider `~/.zshrc` sourced.

    Args: 
        cmd: The exact string that would be typed at the Terminal. (args array is also supported)
        verbose: Print to the screen in real-time.

    Returns:
        output: The exact string that would be printed at the Terminal, including stdout and stderr.
        return_code: The return code.
    """
    # stdout=sp.PIPE, stderr=sp.STDOUT: redirect stderr and stdout to proc.stdout
    # shell=True:               use the shell as the program to execute (`/bin/sh -c`), use a string as command
    # executable='/bin/zsh':    replace default shell /bin/sh to /bin/zsh.
    # text=True:                return stdout and stderr as string instead of bytes
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True, text=True)
    if verbose:
        output_string = ''
        # iter(callable, sentinel): callable is called until it returns the sentinel
        # read(1):                  read one byte from proc.stdout at a time, return an empty bytes object at the end
        for char in iter(lambda: proc.stdout.read(1), ''):
            if verbose:
                sys.stdout.write(char)
            output_string = output_string + char
        return_code = proc.wait()
    else:
        # communicate(): internally waits for the process to complete, return a tuple (stdout, stderr)
        output_string, _ = proc.communicate()
        return_code = proc.returncode
    
    return output_string, return_code


def get_fields_from_card_info(cinfo_json):
    fields = cinfo_json['fields']
    order_0_value = None
    order_1_value = None
    for field in fields.values():
        if field['order'] == 0:
            order_0_value = field['value']
        elif field['order'] == 1:
            order_1_value = field['value']
    return order_0_value, order_1_value

def display_gui():
    pass

try:
    # get card ids
    cid_list = invoke('findCards', query='"deck:English Vocabulary" is:due') # review cards and learning cards waiting to be studied
    print("# of cards waiting for review: ", len(cid_list))
    cid = cid_list[0]

    # get card content
    cinfo_list = invoke("cardsInfo", cards=[cid])
    field_0, field_1 = get_fields_from_card_info(cinfo_list[0])
    field_0 = field_0.replace("<br>", "\n").replace("&nbsp;", " ").replace("\n\n", "\n")
    field_1 = field_1.replace("<br>", "\n").replace("&nbsp;", " ").replace("\n\n", "\n")

    # popup notification
    question_alert_cmd = './alerter -title "Anki - Question" -message ' + shlex.quote(field_0) + ' -actions "Show Answer" -sound default'
    ret, _ = shell(question_alert_cmd)

    # if ret == "@CONTENTCLICKED":
    #     ret = invoke("guiSelectNote", note=cid)
    #     display_gui()
    #     print("display gui")

    if ret == "@CONTENTCLICKED" or ret == "Show Answer":
        md_file = "/tmp/alfred_md_file"
        with open(md_file, "w") as f:
            f.write(field_1)
        alfred_cmd = 'osascript -e \'tell application id "com.runningwithcrayons.Alfred" to run trigger "com.alfredapp.lwh.show" in workflow "com.alfredapp.lwh.chatgpt"\''
        shell(alfred_cmd)
        
        answer_alert_cmd = './alerter -title "Anki" -message ' + shlex.quote(field_1) + ' -actions Again,Hard,Good,Easy -dropdownLabel "====" -sound default'
        ret, _ = shell(answer_alert_cmd)

        if ret == "@CONTENTCLICKED":
            display_gui()
            print("display gui")

        # answer card
        action_list = ["Again", "Hard", "Good", "Easy"]
        if ret in action_list:
            ans = action_list.index(ret) + 1
            print("answer: ", ans)
            # results = invoke("answerCards", answers=[{"cardId": cid, "ease": ans}]) # ease: 1-4
            # if results[0]:
            #     print("review succeed")
            # else:
            #     print("review failed")
except:
    print("something is wrong, did u open Anki?")
