# import the main window object (mw) from aqt
from aqt import mw
from aqt import gui_hooks
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect, restoreGeom, saveGeom
# import all of the Qt GUI library
from aqt.qt import *

from aqt.webview import AnkiWebView
from aqt.operations import QueryOp

from .story_dialog import StoryDialog

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


def add_overview_button(link_handler, links):
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

gui_hooks.overview_will_render_bottom.append(add_overview_button)
