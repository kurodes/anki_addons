# import the main window object (mw) from aqt
from aqt import mw
from aqt import editor
from aqt import gui_hooks
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect, restoreGeom, saveGeom
# import all of the Qt GUI library
from aqt.qt import *

from aqt.webview import AnkiWebView
from aqt.operations import QueryOp

from .story_dialog import StoryDialog
from .init_deck_model import InitDeckModel
from .constants import *
from .openai_helper_stream import gpt_explain_vocabulary

target_deck = mw.addonManager.getConfig(__name__)['TARGET_DECK']

def get_today_words():
    # Note is the data of the fields
    note_ids = []
    # https://docs.ankiweb.net/searching.html
    note_ids.extend(mw.col.find_notes(f"\"deck:{target_deck}\" is:due"))
    note_ids.extend(mw.col.find_notes(f"\"deck:{target_deck}\" is:learn"))
    # note_ids.extend(mw.col.find_notes(f"\"deck:{target_deck}\" is:new"))
    notes = [mw.col.get_note(card_id) for card_id in note_ids]
    words = []
    for note in notes:
        # fields[0], [1] refers to the text of front, back
        question = str(note.fields[0])
        words.append(question)
    return words


def add_button_to_overview(link_handler, links):
    if mw.col.decks.current()['name'] != target_deck:
        return
    links.append(['None', 'compose', 'Compose Story'])
    def custom_link_handler(url):
        if url == 'compose':
            print("hook is called")
            # keywords = get_today_words()
            # dialog = StoryDialog(keywords)
            op = QueryOp(
                parent=mw,
                op = lambda _: get_today_words(),
                success=lambda keywords: StoryDialog(keywords)
            )
            op.with_progress().run_in_background()
        return link_handler(url=url)
    return custom_link_handler

def init_deck_model():
    initiator = InitDeckModel()
    initiator.init()

# init deck, card type and template each time anki is started
gui_hooks.main_window_did_init.append(init_deck_model)

gui_hooks.overview_will_render_bottom.append(add_button_to_overview)

def explain_vocabulary(ed: editor.Editor):
    # if ed.note.note_type()["name"] == NOTE_TYPE_NAME and mw.col.decks.current()['name'] == target_deck: 
    #     print("note type is correct, allow run gpt")
    #     showInfo("note type is correct, allow run gpt")
    # else:
    #     print("note type is uncorrect, return")
    #     showInfo("note type is uncorrect, return")
    vocabulary = ed.note.fields[0]
    print(f"get vocabulary: {vocabulary}")

    def editor_stream_note():
        respond = gpt_explain_vocabulary(vocabulary)
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

    # if mw.col.decks.current()['name'] != target_deck:
    #     return
    button = ed.addButton(
        icon=ICON_PATH,
        cmd="GPT-4",
        func=explain_vocabulary,
        tip="Explain by GPT-4",
        keys="No shortcut"
    )
    buttons.append(button)
    return button

gui_hooks.editor_did_init_buttons.append(add_button_to_editor)
# gui_hooks.editor_did_load_note.append(add_button_to_editor)
