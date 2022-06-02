from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.connect_to_det_model.widgets as card_widgets
import src.connect_to_det_model.functions as card_functions
import src.det_classes.functions as det_classes_functions

from supervisely.app import DataJson, StateJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

import src.sly_globals as g


@card_widgets.connect_det_model_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def connect_to_det_model(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    card_widgets.connect_det_model_button.loading = True
    run_sync(DataJson().synchronize_changes())

    try:
        card_functions.connect_to_model(state)
        DataJson()['det_model_info'] = g.det_model_data.get('info')
        DataJson()['det_model_connected'] = True
        if "sliding_window_support" in g.det_model_data["info"].keys() and g.det_model_data["info"]["sliding_window_support"]:
            state["sliding_window_is_available"] = True
        

        state["selected_classes"] = [True] * len(g.det_model_data["model_meta"].obj_classes)
        det_classes_functions.selected_classes_event(state)
        classes_rows = det_classes_functions.generate_rows()
        det_classes_functions.fill_table(classes_rows)

        DataJson()['current_step'] += 1
        state['collapsed_steps']["det_classes"] = False
    except Exception as ex:
        DataJson()['det_model_connected'] = False
        logger.warn(f'Cannot connect to detection model: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot connect to detection model",
                                                     'message': f'Please reselect detection model and try again'})
    finally:
        card_widgets.connect_det_model_button.loading = False
        run_sync(DataJson().synchronize_changes())
        run_sync(state.synchronize_changes())


@card_widgets.reselect_det_model_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_det_model_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["connect_to_det_model"]
    DataJson()['det_model_connected'] = False
    run_sync(DataJson().synchronize_changes())
