from pathlib import Path

from jinja2 import Environment

from supervisely.app import StateJson, DataJson

import src.sly_globals as g

from src.connect_to_det_model.routes import *
from src.connect_to_det_model.functions import *
from src.connect_to_det_model.widgets import *

DataJson()["model_options"] = {
        "sessionTags": ["deployed_nn"],
        "showLabel": False,
        "size": "small"
}

DataJson()['det_model_info'] = None
DataJson()['det_model_connected'] = False
StateJson()['det_model_id'] = None
