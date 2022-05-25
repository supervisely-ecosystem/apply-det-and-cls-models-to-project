from urllib.parse import urlparse

import supervisely as sly
import src.sly_globals as g
from supervisely import logger


def validate_errors(data):
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def connect_to_model(state):
    model_id = state['det_model_id']
    if model_id is None:
        raise ValueError('det_model_id must be a number')

    g.det_model_data['info'] = validate_errors(g.api.task.send_request(model_id, "get_session_info", data={}))
    g.det_model_data['model_meta'] = sly.ProjectMeta.from_json(
        validate_errors(g.api.task.send_request(model_id, "get_model_meta", data={})))
