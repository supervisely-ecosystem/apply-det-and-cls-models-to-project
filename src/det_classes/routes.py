from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.det_classes.widgets as card_widgets
import src.det_classes.functions as card_functions

from supervisely.app import DataJson, StateJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

import src.sly_globals as g


@card_widgets.select_det_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_det_classes_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    classes_len = len(state["selected_classes"])
    card_widgets.det_classes_done_label.text = f"{classes_len} detection classes selected successfully"
    DataJson()['current_step'] += 1
    #state['collapsed_steps'][""] = False
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())


@card_widgets.reselect_det_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_det_classes_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["det_classes"]
    run_sync(DataJson().synchronize_changes())


@g.app.post('/selected_det_classes_changed/')
def selected_det_classes_changed(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    classes_len = len(state["selected_classes"])
    card_widgets.select_det_classes_button.text = f"SELECT {classes_len} CLASSES"
    if classes_len == 0:
        card_widgets.select_det_classes_button.disabled = True
    else:
        card_widgets.select_det_classes_button.disabled = False
    run_sync(DataJson().synchronize_changes())