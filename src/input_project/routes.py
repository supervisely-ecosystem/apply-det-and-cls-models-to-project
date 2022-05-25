from fastapi import Depends, HTTPException

import supervisely
from supervisely import logger

import src.input_project.widgets as card_widgets
import src.input_project.functions as card_functions

# import src.preferences.widgets as preferences_widgets

from supervisely.app import DataJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

import src.sly_globals as g


@card_widgets.download_project_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def download_selected_project(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    card_widgets.download_project_button.loading = True
    card_widgets.project_selector.disabled = True

    run_sync(DataJson().synchronize_changes())

    try:
        card_functions.download_project(project_selector_widget=card_widgets.project_selector,
                                        state=state, project_dir=g.project_dir)

        g.project['workspace_id'] = card_widgets.project_selector.get_selected_workspace_id(state)
        g.project['project_id'] = card_widgets.project_selector.get_selected_project_id(state)

        card_widgets.project_downloaded_done_label.text = 'Project downloaded'

        DataJson()['current_step'] += 1
    except Exception as ex:
        card_widgets.project_selector.disabled = False

        logger.warn(f'Cannot download project: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot download project",
                                                     'message': f'Please reselect input data and try again'})

    finally:
        card_widgets.download_project_button.loading = False
        run_sync(DataJson().synchronize_changes())


@card_widgets.reselect_project_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_project_button_clicked(state: supervisely.app.StateJson = Depends(supervisely.app.StateJson.from_request)):
    card_widgets.project_selector.disabled = False

    DataJson()['current_step'] = 1
    # preferences_widgets.preview_results_button.disabled = True

    run_sync(DataJson().synchronize_changes())