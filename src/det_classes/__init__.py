from supervisely.app import StateJson, DataJson

import src.sly_globals as g

from src.det_classes.routes import *
from src.det_classes.functions import *
from src.det_classes.widgets import *

DataJson()["classes_table"] = []
StateJson()["selected_classes"] = []
