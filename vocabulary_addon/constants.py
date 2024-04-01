import os
from aqt import mw

DECK_NAME = mw.addonManager.getConfig(__name__)['TARGET_DECK']
NOTE_TYPE_NAME = 'English Vocabulary Model'
NOTE_TYPE_FIELD_NAMES = ['Front', 'Back']
NOTE_TYPE_TEMPLATE_NAME = 'English Vocabulary Template'

ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(ADDON_PATH, "icon.png")
FRONT_TEMPLATE_PATH = os.path.join(ADDON_PATH, 'vocabulary_front_template.html')
BACK_TEMPLATE_PATH = os.path.join(ADDON_PATH, 'vocabulary_back_template.html')

OPENAI_API_KEY = mw.addonManager.getConfig(__name__)['OPENAI_API_KEY']
ENABLE_GPT_4 = mw.addonManager.getConfig(__name__)['ENABLE_GPT_4']

COMPOSE_FONT_SIZE = mw.addonManager.getConfig(__name__)['COMPOSE_FONT_SIZE']
SPEECH_RATE_WPM = mw.addonManager.getConfig(__name__)['SPEECH_RATE_WPM']

SHORTCUT_EXPLAIN_WORD = mw.addonManager.getConfig(__name__)['SHORTCUT_EXPLAIN_WORD']
