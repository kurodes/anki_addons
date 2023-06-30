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
import subprocess
import signal

class StoryDialog(QDialog):
    new_texts_ready= pyqtSignal(str)
    def __init__(self, keywords, parent=None):
        super(StoryDialog, self).__init__(mw if not parent else parent)
        self.keywords = keywords
        self.full_story = ""
        self.sentence_pos = [0]
        self.read_pos = 0
        self.is_playing = True
        self.closing = False
        self.setup_window()
        # self.show_story()
        self.show_story_streamed()
        QueryOp(
            parent=self,
            op = lambda _: self.play_tts(),
            success = lambda _:_
        ).run_in_background()

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

        # Add the controls for sound playing
        self.control_layout = QHBoxLayout()
        self.pause_play_button = QPushButton("Pause")
        self.pause_play_button.clicked.connect(self.toggle_play)
        self.control_layout.addWidget(self.pause_play_button)
        self.prev_button = QPushButton("Prev")
        self.prev_button.clicked.connect(self.prev_play)
        self.control_layout.addWidget(self.prev_button)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_play)
        self.control_layout.addWidget(self.next_button)
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_play)
        self.control_layout.addWidget(self.restart_button)
        self.layout.addLayout(self.control_layout)

        self.close_button = QPushButton("Close")
        qconnect(self.close_button.clicked, self.close)
        self.layout.addWidget(self.close_button)

        qconnect(self.new_texts_ready, self.show_streamed_text)

        self.show()

    def close(self):
        self.closing = True
        self.say_proc.send_signal(signal.SIGINT)
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
        # sentence_buffer = ""
        for delta in story_gen:
            self.full_story += delta
            # sentence_buffer += delta
            self.new_texts_ready.emit(delta)
            # mw.taskman.run_on_main(lambda: self.new_texts_ready.emit(delta))
            if "." in delta:
                self.sentence_pos.append(self.full_story.rindex('.')+1)
                # pos = sentence_buffer.rindex('.')
                # sentence, sentence_buffer = sentence_buffer[:pos+1], sentence_buffer[pos+1:]
                # self.new_texts_ready.emit(sentence)

    def show_streamed_text(self, delta):
        # html_story = self.full_story.replace('\n', '<br>')
        # for word in self.keywords:
        #     html_story = html_story.replace(word, f'<span style="color: #FFFFFF;">{word}</span>')
        # self.text_view.setHtml(html_story)
        # def append_text():
        #     self.text_view.setHtml(html_story)
        # # mw.taskman.run_on_main(append_text)

        # def append_text():
        html_delta = delta.replace('\n', '<br>')
        for word in self.keywords:
            html_delta = html_delta.replace(word, f'<span style="color: #FFFFFF;">{word}</span>')
        cursor = self.text_view.textCursor()  # Get the current cursor
        cursor.movePosition(QTextCursor.MoveOperation.End)  # Move cursor to end of text
        cursor.insertHtml(html_delta)  # Insert the HTML at the current cursor position (end of text)
        # mw.taskman.run_on_main(append_text)
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
            html_content = html_content.replace(word, f'<span style="color: #FFFFFF;">{word}</span>')
        html_content = self.get_html_outline(html_content)
        print(html_content)
        self.text_view.setHtml(html_content)

    def get_html_outline(self, article):
        body = "<p>" + article.replace("\n", "</p><p>") + "</p>"
        body += f'<p><div style="text-align: center;">--- Article Words: {len(article.split())};   Reviewed Words: {len(self.keywords)} ---</div></p>'
        html = "<html><body>" + body +"</body></html>"
        return html

    def toggle_play(self):
        self.say_proc.send_signal(signal.SIGINT)
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.pause_play_button.setText("Pause")
        else:
            self.pause_play_button.setText("Play")
    
    def prev_play(self):
        self.say_proc.send_signal(signal.SIGINT)
        self.read_pos -= 1
        self.highlight_read_sentence()
    
    def next_play(self):
        self.say_proc.send_signal(signal.SIGINT)
        self.read_pos += 1
        self.highlight_read_sentence()
    
    def restart_play(self):
        self.say_proc.send_signal(signal.SIGINT)
        self.read_pos = 0
        # os.system('killall say')
        self.highlight_read_sentence()
    
    def highlight_read_sentence(self):
        st, ed = self.sentence_pos[self.read_pos], self.sentence_pos[self.read_pos+1]
        sentence = self.full_story[st:ed]
        html_story = self.full_story[:st]+'<span style="background-color:#008B8B;">'+sentence+'</span>'+self.full_story[ed:]
        html_story = html_story.replace('\n', '<br>')
        for word in self.keywords:
            html_story = html_story.replace(word, f'<span style="color: #FFFFFF;">{word}</span>')
        scroll_pos = self.text_view.verticalScrollBar().value()
        self.text_view.setHtml(html_story)
        self.text_view.verticalScrollBar().setValue(scroll_pos)

    def play_tts(self):
        rate = mw.addonManager.getConfig(__name__)['SPEECH_RATE_WPM']
        while True:
            if self.closing:
                break
            if self.is_playing:
                if len(self.sentence_pos) > self.read_pos + 1:
                    mw.taskman.run_on_main(self.highlight_read_sentence)
                    sentence = self.full_story[self.sentence_pos[self.read_pos]:self.sentence_pos[self.read_pos+1]]
                    # os.system(f'say -r {rate} "{sentence}"')
                    self.say_proc = subprocess.Popen(['say', '-r', str(rate), sentence])
                    ret_code = self.say_proc.wait()
                    if ret_code == 0:
                        self.read_pos += 1
            sleep(0.1)
