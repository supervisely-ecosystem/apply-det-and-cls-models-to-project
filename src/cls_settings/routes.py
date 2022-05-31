import supervisely as sly
from supervisely import logger
from supervisely.app import DataJson
from supervisely.app.fastapi import run_sync
from supervisely.app.widgets import ElementButton

from fastapi import Depends, HTTPException

import src.cls_settings.functions as card_functions

import src.cls_settings.widgets as card_widgets
import src.input_project.widgets as input_project_widgets
import src.connect_to_det_model.widgets as connect_det_model_widgets
import src.det_classes.widgets as det_classes_widgets
import src.det_settings.widgets as det_settings_widgets
import src.connect_to_cls_model.widgets as connect_cls_model_widgets

import src.sly_functions as f
import src.sly_globals as g


@card_widgets.select_cls_settings_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_cls_settings_button_clicked(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    try:
        if state['selectedLabelingMode'] == "Classes" and len(state['selectedClasses']) == 0:
            raise ValueError('classes not selected')

        g.selected_classes_list = state['selectedClasses'] # TODO
        DataJson()['labelingDone'] = False
        DataJson()['labelingStarted'] = False

        card_widgets.preview_cls_results_button.disabled = True

        state['collapsed_steps']["output_data"] = False
        DataJson()['current_step'] += 1
    except Exception as ex:
        logger.warn(f'Cannot select preferences: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot select preferences",
                                                     'message': f'{ex}'})
    finally:
        run_sync(DataJson().synchronize_changes())
        run_sync(state.synchronize_changes())


@card_widgets.start_labeling_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def start_labeling_button_clicked(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    card_widgets.start_labeling_button.loading = True

    input_project_widgets.reselect_project_button.disabled = True
    connect_det_model_widgets.reselect_det_model_button.disabled = True
    det_classes_widgets.reselect_det_classes_button.disabled = True
    det_settings_widgets.reselect_det_settings_button.disabled = True
    connect_cls_model_widgets.reselect_cls_model_button.disabled = True
    card_widgets.preview_cls_results_button.disabled = True
    card_widgets.reselect_cls_settings_button.disabled = True

    DataJson()['labelingDone'] = False
    DataJson()['labelingStarted'] = True

    run_sync(DataJson().synchronize_changes())

    try:
        #state['selectedClasses'] = g.selected_det_for_cls_classes  # TODO: till Umar fixing state replacing
        if state['selectedLabelingMode'] == "Classes" and \
            (len(state['selectedClasses']) == 0 or \
            not any(state['selectedClasses'])):
            raise ValueError('Classes not selected')

        g.selected_det_for_cls_classes = []
        for class_ind, obj_class in enumerate(g.det_model_data["model_meta"].obj_classes):
            if state["selectedClasses"][class_ind]:
                g.selected_det_for_cls_classes.append(obj_class.name)

        g.cls_model_tag_suffix = ''
        g.updated_images_ids = set()

        card_functions.label_project(state=state)
        card_functions.upload_project()

        DataJson()['labelingDone'] = True

    except Exception as ex:
        logger.warn(f'Cannot start labeling: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot start labeling",
                                                     'message': f'{ex}'})
    finally:
        DataJson()['labelingStarted'] = False

        input_project_widgets.reselect_project_button.disabled = False
        connect_det_model_widgets.reselect_det_model_button.disabled = False
        det_classes_widgets.reselect_det_classes_button.disabled = False
        det_settings_widgets.reselect_det_settings_button.disabled = False
        connect_cls_model_widgets.reselect_cls_model_button.disabled = False
        card_widgets.preview_cls_results_button.disabled = False
        card_widgets.reselect_cls_settings_button.disabled = False

        card_widgets.start_labeling_button.loading = False
        run_sync(DataJson().synchronize_changes())


@card_widgets.reselect_cls_settings_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def reselect_cls_settings_button_clicked(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    DataJson()['current_step'] = DataJson()['steps']['cls_settings']
    card_widgets.preview_cls_results_button.disabled = False
    run_sync(DataJson().synchronize_changes())


@card_widgets.preview_cls_results_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def preview_cls_results_button_clicked(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    
    state["preview_is_available"] = True
    
    card_widgets.preview_cls_results_button.loading = True
    card_widgets.preview_grid_gallery.loading = True
    run_sync(DataJson().synchronize_changes())
    run_sync(state.synchronize_changes())
    try:
        if state['selectedLabelingMode'] == "Classes" and \
            (len(state['selectedClasses']) == 0 or \
            not any(state['selectedClasses'])):
            raise ValueError('Classes not selected')

        g.selected_det_for_cls_classes = []
        for class_ind, obj_class in enumerate(g.det_model_data["model_meta"].obj_classes):
            if state["selectedClasses"][class_ind]:
                g.selected_det_for_cls_classes.append(obj_class.name)

        if state['selectedLabelingMode'] == "Classes" and \
            (g.preview_boxes is None or \
            g.preview_image is None or \
            not g.preview_boxes):
            state["preview_is_available"] = False
        if state['selectedLabelingMode'] == "Classes":
            selected_labels = []
            for label in g.preview_boxes:
                if label.obj_class.name in g.selected_det_for_cls_classes:
                    selected_labels.append(label)
            if not len(selected_labels):
                state["preview_is_available"] = False
        run_sync(state.synchronize_changes())
        if not state["preview_is_available"]:
            raise ValueError("No boxes of selected classes on image for preview.")
        g.cls_model_tag_suffix = ''
        g.updated_images_ids = set()

        images_for_preview = card_functions.get_images_for_preview(state=state, img_num=6)

        card_widgets.preview_grid_gallery.clean_up()

        for current_image in images_for_preview:
            card_widgets.preview_grid_gallery.append(
                image_url=current_image['url'],
                title=current_image['title']
            )


    except Exception as ex:
        logger.warn(f'Cannot preview results: {repr(ex)}', exc_info=True)
        raise HTTPException(status_code=500, detail={'title': "Cannot preview results",
                                                     'message': f'{ex}'})
    finally:
        card_widgets.preview_cls_results_button.loading = False
        card_widgets.preview_grid_gallery.loading = False
        run_sync(DataJson().synchronize_changes())


@g.app.post('/classes_selection_change/')
def selected_classes_changed(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    pass
    # if len(state['selectedClasses']) > 0:
    #     card_widgets.select_preferences_button.disabled = False
    # else:
    #     card_widgets.select_preferences_button.disabled = True

    # run_sync(state.synchronize_changes())
    # run_sync(DataJson().synchronize_changes())

@card_widgets.select_all_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def select_all_classes_button_clicked(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    state["selectedClasses"] = [True] * len(g.det_model_data["model_meta"].obj_classes)
    run_sync(state.synchronize_changes())

@card_widgets.deselect_all_classes_button.add_route(app=g.app, route=ElementButton.Routes.BUTTON_CLICKED)
def deselect_all_classes_button_clicked(state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    state["selectedClasses"] = [False] * len(g.det_model_data["model_meta"].obj_classes)
    run_sync(state.synchronize_changes())