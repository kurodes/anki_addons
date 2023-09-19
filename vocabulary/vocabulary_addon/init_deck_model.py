from aqt import mw
from aqt.operations import CollectionOp
import os
import re

# Create a deck, model, and template if they do not already exist. If the template does exist, update it.
class InitDeckModel:
    def __init__(self):
        self.deck_name = mw.addonManager.getConfig(__name__)['TARGET_DECK']
        self.model_name = 'English Vocablary Model'
        self.field_names = ['Front', 'Back']
        self.template_name = 'English Vocabulary Template'
        self.front_template = None
        self.back_template = None
        self.deck_id = None
        self.model = None

    def init_deck(self):
        self.deck_id = mw.col.decks.id(self.deck_name, create=False)
        if self.deck_id is None:
            self.deck_id = mw.col.decks.id(self.deck_name)
        mw.col.decks.select(self.deck_id)

    def init_model(self):
        self.model = mw.col.models.by_name(self.model_name)

        # load template from file
        current_path = os.path.dirname(os.path.abspath(__file__))
        openai_api_key = mw.addonManager.getConfig(__name__)['OPENAI_API_KEY']
        with open(os.path.join(current_path, 'vocabulary_front_template.html'), 'r') as file:
            self.front_template = re.sub(r'Authorization: "(.*?)"', f'Authorization: "Bearer {openai_api_key}"', file.read())
        with open(os.path.join(current_path, 'vocabulary_back_template.html'), 'r') as file:         
            self.back_template = file.read()

        if self.model is None:
            # create new model (note type)
            self.model = mw.col.models.new(self.model_name)
            # add fields to model (note type)
            for field_name in self.field_names:
                field = mw.col.models.new_field(field_name)
                mw.col.models.add_field(self.model, field)
            # add template to model (note type)
            template = mw.col.models.new_template(self.template_name)
            template['qfmt'] = self.front_template
            template['afmt'] = self.back_template
            mw.col.models.add_template(self.model, template)
        else:
            # update template of model (note type)
            if self.model['tmpls'][0]['qfmt'] != self.front_template:
                self.model['tmpls'][0]['qfmt'] = self.front_template
            if self.model['tmpls'][0]['afmt'] != self.back_template:
                self.model['tmpls'][0]['afmt'] = self.back_template

        # Save the changes
        mw.col.models.save(self.model)

    def init(self):
        self.init_deck()
        self.init_model()
        # mw.reset()
