from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.connect_to_cls_model.widgets as card_widgets
import src.connect_to_cls_model.functions as card_functions
# import src.det_classes.functions as det_classes_functions

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
        DataJson()['cls_model_info'] = g.cls_model_data.get('info')
        DataJson()['cls_model_connected'] = True

        #classes_rows = det_classes_functions.generate_rows()
        #det_classes_functions.fill_table(classes_rows)

        DataJson()['current_step'] += 1
        #state['collapsed_steps']["det_classes"] = False
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
    DataJson()['cls_model_connected'] = False
    run_sync(DataJson().synchronize_changes())
