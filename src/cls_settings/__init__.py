from pathlib import Path

from jinja2 import Environment

from supervisely.app import StateJson, DataJson

import src.sly_globals as g

from src.cls_settings.routes import *
from src.cls_settings.functions import *
from src.cls_settings.widgets import *


StateJson()['selectedLabelingMode'] = "Classes"
StateJson()['outputProject'] = "New"
StateJson()['padding'] = 0
StateJson()['topN'] = 1
StateJson()['addConfidence'] = True
StateJson()['addSuffix'] = False
StateJson()['suffixValue'] = None

StateJson()['selectedClasses'] = []
DataJson()['classes_table_content'] = []
StateJson()["preview_is_available"] = True

DataJson()['outputProject'] = {
    'id': None
}

DataJson()['labelingStarted'] = False
DataJson()['labelingDone'] = False



