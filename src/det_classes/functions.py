import src.sly_globals as g
from supervisely.app import DataJson
from supervisely.app.fastapi import run_sync

def generate_rows():
    rows = []
    obj_classes = g.det_model_data["model_meta"].obj_classes
    for obj_class in obj_classes:
        rows.append(
            {
                'label': f'{obj_class.name}',
                'shapeType': f'{obj_class.geometry_type.geometry_name()}',
                'color': f'{"#%02x%02x%02x" % tuple(obj_class.color)}',
            }
        )
    return rows


def fill_table(table_rows):
    # TODO: check recursive=False
    DataJson()["classes_table"] = table_rows
    run_sync(DataJson().synchronize_changes())