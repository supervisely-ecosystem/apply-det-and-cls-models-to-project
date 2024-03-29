from supervisely.app import DataJson, StateJson
from supervisely.app.widgets import (
    ProjectSelector,
    ElementButton,
    SlyTqdm,
    DoneLabel,
    NotificationBox,
    GridGallery,
    InputNumber,
)

import src.sly_globals as g

select_cls_settings_button = ElementButton(text="Confirm settings")
reselect_cls_settings_button = ElementButton(
    text='<i style="margin-right: 5px" class="zmdi zmdi-rotate-left"></i>Reselect settings',
    button_type="warning",
    button_size="small",
    plain=True,
)

preview_cls_results_button = ElementButton(
    text='<i class="zmdi zmdi-collection-image" style="margin-right: 5px"></i> Preview results',
    button_type="warning",
    button_size="small",
)
preview_cls_results_button.disabled = True

preview_is_not_available_infobox = NotificationBox(
    title="Preview is not available",
    description="No boxes of selected classes on image for preview",
    box_type="warning",
)
select_all_classes_button = ElementButton(
    text='<i class="zmdi zmdi-check-all"></i> SELECT ALL',
    button_type="text",
    button_size="mini",
    plain=True,
)
deselect_all_classes_button = ElementButton(
    text='<i class="zmdi zmdi-square-o"></i> DESELECT ALL',
    button_type="text",
    button_size="mini",
    plain=True,
)
preview_grid_gallery = GridGallery(
    columns_number=3, show_opacity_slider=False, sync_views=True
)

batch_size_input = InputNumber(value=g.batch_size, min=1, max=128, step=1)

labeling_progress = SlyTqdm()
labeling_done_label = DoneLabel(text="done")
start_labeling_button = ElementButton(text="APPLY MODELS TO PROJECT")
