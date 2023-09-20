from aqt import mw, editor
from aqt.operations import QueryOp

from .constants import *
from .openai_helper_stream import gpt_explain_vocabulary_stream


def explain_vocabulary(ed: editor.Editor):
    # if ed.note.note_type()["name"] == NOTE_TYPE_NAME and mw.col.decks.current()['name'] == DECK_NAME: 
    #     showInfo("note type is correct, allow run gpt")
    vocabulary = ed.note.fields[0]
    print(f"get vocabulary: {vocabulary}")

    def editor_stream_note():
        respond = gpt_explain_vocabulary_stream(vocabulary)
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
        cmd="GPT-4",
        func=explain_vocabulary,
        tip="Explain by GPT-4",
        keys="No shortcut"
    )
    buttons.append(button)
    return button
