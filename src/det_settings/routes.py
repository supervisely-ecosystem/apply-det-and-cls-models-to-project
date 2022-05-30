from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.det_settings.widgets as card_widgets
import src.det_settings.functions as card_functions
import src.sly_functions as global_functions

from supervisely.app import DataJson, StateJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

import src.sly_globals as g

import random


@card_widgets.show_det_preview_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def show_det_preview_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['videoUrl'] = None
    state['previewLoading'] = True
    card_widgets.show_det_preview_button.loading = True
    card_widgets.show_det_preview_button.text = "DOING INFERENCE"
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())

    image_info = random.choice(g.images_info)
    card_functions.check_sliding_sizes_by_image(state, image_info)
    # TODO: message about vis

    # TODO: select random or specified image
    inf_settings = {
        "conf_thres": state["conf_thres"],
        "iou_thres": state["iou_thres"],
        "inference_mode": state["inference_mode"],
        "sliding_window_params": {
            "windowHeight": state["windowHeight"],
            "windowWidth": state["windowWidth"],
            "overlapY": state["overlapY"],
            "overlapX": state["overlapX"],
            "borderStrategy": state["borderStrategy"]
        }
    }
    ann_pred_res = global_functions.validate_response_errors(
        g.api.task.send_request(
            state['det_model_id'], 
            "inference_image_id",
            data={
                "image_id": image_info.id,
                "settings": inf_settings
            }, 
            timeout=g.model_inference_timeout
        )
    )
    if isinstance(ann_pred_res, dict) and "data" in ann_pred_res.keys():
        predictions = ann_pred_res["data"]["slides"]
    else:
        # TODO: raise error
        pass
    card_widgets.show_det_preview_button.text = "WRITING VIDEO"
    run_sync(DataJson().synchronize_changes())

    img = g.api.image.download_np(image_info.id)
    file_info = card_functions.write_video(state, img, predictions)

    DataJson()['videoUrl'] = file_info.full_storage_url
    state['previewLoading'] = False
    card_widgets.show_det_preview_button.text = "PREVIEW"
    card_widgets.show_det_preview_button.loading = False
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())


@card_widgets.select_inference_mode_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_inference_mode_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] += 1
    state['collapsed_steps']["connect_to_cls_model"] = False
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())



@card_widgets.reselect_inference_mode_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_inference_mode_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["det_inference_mode"]
    run_sync(DataJson().synchronize_changes())