from supervisely.app import StateJson, DataJson

import src.sly_globals as g

from src.det_settings.routes import *
from src.det_settings.functions import *
from src.det_settings.widgets import *

DataJson()["videoUrl"] = None

StateJson()["conf_thres"] = 0.5
StateJson()["iou_thres"] = 0.5
StateJson()["windowHeight"] = 256
StateJson()["inference_mode"] = "full" # ["full", "sliding_window"]
StateJson()["windowHeight"] = 256
StateJson()["windowWidth"] = 256
StateJson()["overlapY"] = 32
StateJson()["overlapX"] = 32
StateJson()["borderStrategy"] = "shift_window"  # ["shift_window", "add_padding", "change_size"]
StateJson()["fps"] = 4

StateJson()["progress"] = 0
StateJson()["progressCurrent"] = 0
StateJson()["progressTotal"] = 0

StateJson()["previewLoading"] = False
StateJson()["progressPreview"] = 0
StateJson()["progressPreviewMessage"] = "Rendering frames"
StateJson()["progressPreviewCurrent"] = 0
StateJson()["progressPreviewTotal"] = 0
StateJson()["randomImagePreview"] = True
StateJson()["previewOnImageId"] = None
DataJson()["imagesForPreview"] = None
DataJson()["full_preview_is_available"] = False