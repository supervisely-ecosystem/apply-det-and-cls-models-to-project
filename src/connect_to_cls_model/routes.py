from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.connect_to_cls_model.widgets as card_widgets
import src.connect_to_cls_model.functions as card_functions

import src.cls_settings.functions as cls_settings_functions
import src.cls_settings.widgets as cls_settings_widgets

from supervisely.app import DataJson, StateJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

import src.sly_globals as g


@card_widgets.connect_cls_model_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def connect_to_cls_model(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    card_widgets.connect_cls_model_button.loading = True
    run_sync(DataJson().synchronize_changes())

    try:
        card_functions.connect_to_model(state)
        DataJson()['modelClasses'] = card_functions.get_model_classes_list()
        DataJson()['classes_table_content'] = cls_settings_functions.get_classes_table_content()
        cls_settings_widgets.preview_cls_results_button.disabled = False
        state["selectedClasses"] = [False] * len(g.det_model_data["model_meta"].obj_classes)
        DataJson()['cls_model_info'] = g.cls_model_data.get('info')
        DataJson()['cls_model_connected'] = True

        DataJson()['current_step'] += 1
        state['collapsed_steps']["cls_settings"] = False
    except Exception as ex:
        DataJson()['cls_model_connected'] = False
        logger.warn(f'Cannot connect to classification model: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot connect to classification model",
                                                     'message': f'Please reselect classification model and try again'})
    finally:
        card_widgets.connect_cls_model_button.loading = False
        run_sync(DataJson().synchronize_changes())
        run_sync(state.synchronize_changes())


@card_widgets.reselect_cls_model_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_cls_model_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["connect_to_cls_model"]
    cls_settings_widgets.preview_cls_results_button.disabled = True
    DataJson()['cls_model_connected'] = False
    run_sync(DataJson().synchronize_changes())


@g.app.post('/toggle_all_classes/')
def toggle_all_classes(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    if DataJson()['all_classes_collapsed'] is True:
        # card_widgets.toggle_all_previews_button.text = 'hide all'
        state['activeNames'] = [class_info['name'] for class_info in DataJson()['modelClasses']]
    else:
        # card_widgets.toggle_all_previews_button.text = 'show all'
        state['activeNames'] = []

    DataJson()['all_classes_collapsed'] = not DataJson()['all_classes_collapsed']
    run_sync(state.synchronize_changes())
    run_sync(DataJson().synchronize_changes())