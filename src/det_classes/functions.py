import src.sly_globals as g
from supervisely.app import DataJson
from supervisely.app.fastapi import run_sync

import src.det_classes.widgets as card_widgets


def selected_classes_event(state):
    g.selected_det_classes = []
    for idx, obj_class in enumerate(g.det_model_data["model_meta"].obj_classes):
        if state["selected_classes"][idx]:
            g.selected_det_classes.append(obj_class.name)
    classes_len = len(g.selected_det_classes)
    card_widgets.select_det_classes_button.text = f"SELECT {classes_len} CLASSES"
    if classes_len == 0:
        card_widgets.select_det_classes_button.disabled = True
    else:
        card_widgets.select_det_classes_button.disabled = False
    run_sync(DataJson().synchronize_changes())


def generate_rows():
    rows = []
    obj_classes = g.det_model_data["model_meta"].obj_classes
    for obj_class in obj_classes:
        rows.append(
            {
                'name': f'{obj_class.name}',
                'shape': f'{obj_class.geometry_type.geometry_name()}',
                'color': f'{"#%02x%02x%02x" % tuple(obj_class.color)}',
            }
        )
    return rows


def fill_table(table_rows):
    # TODO: check recursive=False
    DataJson()["classes_table"] = table_rows
    run_sync(DataJson().synchronize_changes())