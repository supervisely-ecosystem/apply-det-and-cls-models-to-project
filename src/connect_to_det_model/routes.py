from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.connect_to_det_model.widgets as card_widgets
import src.connect_to_det_model.functions as card_functions

#import src.preferences.functions as preferences_functions
#import src.preferences.widgets as preferences_widgets

from supervisely.app import DataJson
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
        #preferences_widgets.preview_results_button.disabled = False

        DataJson()['current_step'] += 1
    except Exception as ex:
        DataJson()['det_model_connected'] = False
        logger.warn(f'Cannot connect to detection model: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot connect to detection model",
                                                     'message': f'Please reselect detection model and try again'})
    finally:
        card_widgets.connect_det_model_button.loading = False
        run_sync(DataJson().synchronize_changes())


@card_widgets.reselect_det_model_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_det_model_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()["steps"]["connect_to_det_model"]
    DataJson()['det_model_connected'] = False
    #preferences_widgets.preview_results_button.disabled = True
    run_sync(DataJson().synchronize_changes())
