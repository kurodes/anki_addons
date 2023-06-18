# import the main window object (mw) from aqt
from aqt import mw
from aqt import gui_hooks
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect, restoreGeom, saveGeom
# import all of the Qt GUI library
from aqt.qt import *

from aqt.webview import AnkiWebView
from aqt.operations import QueryOp

from .openai_helper import gpt_compose_story

target_deck = mw.addonManager.getConfig(__name__)['TARGET_DECK']

def get_today_words():
    # Card & Note
    # Card is rendered by the template and css
    #   find_cards(), get_card(), card.question(), card.answer()
    # Note is the data of the fields
    note_ids = []
    # https://docs.ankiweb.net/searching.html
    note_ids.extend(mw.col.find_notes(f"\"deck:{target_deck}\" is:due"))
    note_ids.extend(mw.col.find_notes(f"\"deck:{target_deck}\" is:new"))
    notes = [mw.col.get_note(card_id) for card_id in note_ids]
    words = []
    for note in notes:
        # fields[0], [1] refers to the text of front, back
        question = str(note.fields[0])
        words.append(question)
    return words

class StoryDialog(QDialog):
    def __init__(self, parent=None): # todo: parent=mw
        super(StoryDialog, self).__init__(parent)

        self.keywords = get_today_words()

        self.layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        self.setWindowTitle("Composed Story")

        # self.web_view = AnkiWebView()
        # self.layout.addWidget(self.web_view)

        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setStyleSheet("font-size: 18px; padding: 20px;")
        self.layout.addWidget(self.text_view)

        self.close_button = QPushButton("Close")
        qconnect(self.close_button.clicked, self.close)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)
        self.resize(1000,800)
        restoreGeom(self, "composed articles")
        
        # self.text_view.setHtml(self.get_html_outline("Composing story..."))

        self.compose_and_display_story()

    def close(self):
        saveGeom(self, "composed articles")
        self.reject()
        
    def compose_and_display_story(self):
        op = QueryOp(
            parent=self,
            op = lambda _: gpt_compose_story(self.keywords),
            success=self.display_story
        )
        op.with_progress().run_in_background()

    def display_story(self, story):
        html_content = story
        for word in self.keywords:
            # html_content = html_content.replace(word, f'<input type="checkbox" id="{word}" value="{word}"><span style="color: red;">{word}</span></input>')
            html_content = html_content.replace(word, f'<span style="color: #50C878;">{word}</span>')
        html_content = self.get_html_outline(html_content)
        print(html_content)
        self.text_view.setHtml(html_content)
        # self.text_view.setHtml(story)
        self.exec()

    def get_html_outline(self, article):
        body = "<p>" + article.replace("\n", "</p><p>") + "</p>"
        body += f'<p><div style="text-align: center;">--- Article Words: {len(article.split())};   Reviewed Words: {len(self.keywords)} ---</div></p>'
        html = "<html><body>" + body +"</body></html>"
        return html

def add_overview_button(link_handler, links):
    if mw.col.decks.current()['name'] != target_deck:
        return
    links.append(['None', 'compose', 'Compose Story'])

    def custom_link_handler(url):
        if url == 'compose':
            print("hook is called")
            dialog = StoryDialog()
        return link_handler(url=url)
    return custom_link_handler

gui_hooks.overview_will_render_bottom.append(add_overview_button)
