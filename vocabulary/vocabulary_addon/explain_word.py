from aqt import mw, editor
from aqt.operations import QueryOp

from .constants import *
from .openai_helper_stream import gpt_explain_word_stream

import os

def explain_word(ed: editor.Editor):
    # if ed.note.note_type()["name"] == NOTE_TYPE_NAME and mw.col.decks.current()['name'] == DECK_NAME: 
    #     showInfo("note type is correct, allow run gpt")
    vocabulary = ed.note.fields[0]
    print(f"get vocabulary: {vocabulary}")

    def editor_stream_note():
        respond = gpt_explain_word_stream(vocabulary)
        os.system(f"""
APP_BUNDLE_ID=com.eusoft.eudic
open -b $APP_BUNDLE_ID
open -b $APP_BUNDLE_ID
osascript <<EOD
    tell application id "$APP_BUNDLE_ID"
        activate
        show dic with word "{vocabulary}"
    end tell
EOD
""")
        for delta in respond:
            html_delta = delta.replace('\n', '<br>')
            ed.note.fields[1] += html_delta
            mw.taskman.run_on_main(lambda: ed.loadNote())

    QueryOp(
        parent=mw,
        op=lambda _: editor_stream_note(),
        success=lambda _: None
    ).run_in_background()


def add_button_to_editor(buttons: list[str], ed: editor.Editor):
    # show button on all editor mode: add_cards, browser, editcurrent
    # if ed.editorMode == editor.EditorMode.ADD_CARDS:
    # if mw.col.decks.current()['name'] != DECK_NAME:
    button = ed.addButton(
        icon=ICON_PATH,
        cmd="explain_word_button", # innder index: cmd -> func
        func=explain_word,
        tip=f"Learn With GPT-4 ({SHORTCUT_EXPLAIN_WORD})",
        keys=SHORTCUT_EXPLAIN_WORD # add shortcut
    )
    buttons.append(button)
    return button

# def add_shortcut_to_editor_button(shortcuts: list[tuple], ed: editor.Editor):
#     print("Shortcut added")
#     shortcuts.append((SHORTCUT_EXPLAIN_WORD, lambda ed=ed: explain_word(ed)))
