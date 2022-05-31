from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.det_classes.widgets as card_widgets
import src.det_classes.functions as card_functions
import src.det_settings.functions as det_settings_functions

from supervisely.app import DataJson, StateJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

import src.sly_globals as g


@card_widgets.select_det_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_det_classes_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    classes_len = len(g.selected_det_classes)
    card_widgets.det_classes_done_label.text = f"{classes_len} detection classes selected successfully"
    DataJson()["imagesForPreview"] = det_settings_functions.get_images_for_preview_list()
    DataJson()['current_step'] += 1
    state['collapsed_steps']["det_settings"] = False
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())


@card_widgets.reselect_det_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_det_classes_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["det_classes"]
    run_sync(DataJson().synchronize_changes())


@g.app.post('/selected_det_classes_changed/')
def selected_det_classes_changed(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    card_functions.selected_classes_event(state)


@card_widgets.select_all_det_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_all_det_classes_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    state["selected_classes"] = [True] * len(g.det_model_data["model_meta"].obj_classes)
    run_sync(state.synchronize_changes())
    card_functions.selected_classes_event(state)
    

@card_widgets.deselect_all_det_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def deselect_all_det_classes_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    state["selected_classes"] = [False] * len(g.det_model_data["model_meta"].obj_classes)
    run_sync(state.synchronize_changes())
    card_functions.selected_classes_event(state)