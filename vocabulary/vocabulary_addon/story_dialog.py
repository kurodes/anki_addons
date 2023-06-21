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
from .openai_helper_stream import gpt_compose_story_stream

from time import sleep

class StoryDialog(QDialog):
    new_texts_ready= pyqtSignal(str)
    def __init__(self, keywords, parent=None):
        super(StoryDialog, self).__init__(mw if not parent else parent)
        self.keywords = keywords
        self.full_story = ""
        self.setup_window()
        # self.show_story()
        self.show_story_streamed()

    def setup_window(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Composed Story")
        self.resize(1000,800)
        restoreGeom(self, "composed articles")

        # self.web_view = AnkiWebView()
        # self.layout.addWidget(self.web_view)
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setStyleSheet(f"font-size: {mw.addonManager.getConfig(__name__)['FONT_SIZE']}px; padding: 20px;")
        self.layout.addWidget(self.text_view)

        self.close_button = QPushButton("Close")
        qconnect(self.close_button.clicked, self.close)
        self.layout.addWidget(self.close_button)

        qconnect(self.new_texts_ready, self.show_streamed_text)

        self.show()

    def close(self):
        saveGeom(self, "composed articles")
        self.reject()

    def show_story_streamed(self):
        QueryOp(
            parent=self,
            op=lambda _: self.emit_streamed_text(),
            success=lambda _: self.show_streamed_text(f'<br><div style="text-align: center;">--- Article Words: {len(self.full_story.split())};   Reviewed Words: {len(self.keywords)} ---</div>')
        ).run_in_background()

    def emit_streamed_text(self):
        story_gen = gpt_compose_story_stream(self.keywords)
        for delta in story_gen:
            self.full_story += delta
            self.new_texts_ready.emit(delta)
            # mw.taskman.run_on_main(lambda: self.new_texts_ready.emit(delta))

    def show_streamed_text(self, delta):
        html_delta = delta.replace('\n', '<br>')
        for word in self.keywords:
            html_delta = html_delta.replace(word, f'<span style="color: #50C878;">{word}</span>')
        cursor = self.text_view.textCursor()  # Get the current cursor
        cursor.movePosition(QTextCursor.MoveOperation.End)  # Move cursor to end of text
        cursor.insertHtml(html_delta)  # Insert the HTML at the current cursor position (end of text)
        # self.text_view.setTextCursor(cursor)  # Update the QTextEdit's cursor

    def show_story(self):
        op = QueryOp(
            parent=self,
            op = lambda _: gpt_compose_story(self.keywords),
            success=self.show_text
        )
        op.with_progress().run_in_background()

    def show_text(self, text):
        html_content = text
        self.keywords.append("the")
        for word in self.keywords:
            # html_content = html_content.replace(word, f'<input type="checkbox" id="{word}" value="{word}"><span style="color: red;">{word}</span></input>')
            html_content = html_content.replace(word, f'<span style="color: #50C878;">{word}</span>')
        html_content = self.get_html_outline(html_content)
        print(html_content)
        self.text_view.setHtml(html_content)

    def get_html_outline(self, article):
        body = "<p>" + article.replace("\n", "</p><p>") + "</p>"
        body += f'<p><div style="text-align: center;">--- Article Words: {len(article.split())};   Reviewed Words: {len(self.keywords)} ---</div></p>'
        html = "<html><body>" + body +"</body></html>"
        return html
