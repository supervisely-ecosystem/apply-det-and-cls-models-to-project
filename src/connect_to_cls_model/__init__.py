from pathlib import Path

from jinja2 import Environment

from supervisely.app import StateJson, DataJson

import src.sly_globals as g

from src.connect_to_cls_model.routes import *
from src.connect_to_cls_model.functions import *
from src.connect_to_cls_model.widgets import *

DataJson()["cls_model_options"] = {
        "sessionTags": ["deployed_nn_cls"],
        "showLabel": False,
        "size": "small"
}

DataJson()['cls_model_info'] = None
DataJson()['cls_model_connected'] = False
StateJson()['cls_model_id'] = None
