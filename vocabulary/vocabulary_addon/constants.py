import os
# from aqt import mw

ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(ADDON_PATH, "icon.png")
NOTE_TYPE_NAME = 'English Vocablary Model'
NOTE_TYPE_FIELD_NAMES = ['Front', 'Back']
NOTE_TYPE_TEMPLATE_NAME = 'English Vocabulary Template'

# OPENAI_API_KEY = mw.addonManager.getConfig(__name__)['OPENAI_API_KEY']


