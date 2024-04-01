import os
import re
from aqt import mw

from .constants import *


# Create a deck, model, and template if they do not already exist. If the template does exist, update it.
def init_deck_model_template():
    # init deck
    deck_id = mw.col.decks.id(DECK_NAME, create=False)
    if deck_id is None:
        deck_id = mw.col.decks.id(DECK_NAME)
    mw.col.decks.select(deck_id)

    # init or update model
    with open(FRONT_TEMPLATE_PATH, 'r') as file:
        front_template = re.sub(r'Authorization: "(.*?)"', f'Authorization: "Bearer {OPENAI_API_KEY}"', file.read())
    with open(BACK_TEMPLATE_PATH, 'r') as file:
        back_template = file.read()
    model = mw.col.models.by_name(NOTE_TYPE_NAME)
    if model is None:
        # create new model (note type)
        model = mw.col.models.new(NOTE_TYPE_NAME)
        # add fields to model (note type)
        for field_name in NOTE_TYPE_FIELD_NAMES:
            field = mw.col.models.new_field(field_name)
            mw.col.models.add_field(model, field)
        # add template to model (note type)
        template = mw.col.models.new_template(NOTE_TYPE_TEMPLATE_NAME)
        template['qfmt'] = front_template
        template['afmt'] = back_template
        mw.col.models.add_template(model, template)
    else:
        # update template of model (note type)
        if model['tmpls'][0]['qfmt'] != front_template:
            model['tmpls'][0]['qfmt'] = front_template
        if model['tmpls'][0]['afmt'] != back_template:
            model['tmpls'][0]['afmt'] = back_template
    # Save the changes
    mw.col.models.save(model)
