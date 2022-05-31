from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger
import copy

import src.det_settings.widgets as card_widgets
import src.det_settings.functions as card_functions

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
    state["previewOnImageId"] = g.images_info[0].id if len(g.images_info) > 0 else None
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())
    with card_widgets.det_preview_progress(message='Inference...', total=1) as pbar:
        image_info, predictions = card_functions.get_preview_predictions(state)
        pbar.update()

    run_sync(DataJson().synchronize_changes())
    img = g.api.image.download_np(image_info.id)
    file_info = card_functions.write_video(state, img, predictions)

    DataJson()['videoUrl'] = file_info.full_storage_url
    state['previewLoading'] = False
    card_widgets.show_det_preview_button.loading = False
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())


@card_widgets.select_det_settings_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_det_settings_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] += 1
    state['collapsed_steps']["connect_to_cls_model"] = False
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())


@card_widgets.reselect_det_settings_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_det_settings_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["det_settings"]
    run_sync(DataJson().synchronize_changes())