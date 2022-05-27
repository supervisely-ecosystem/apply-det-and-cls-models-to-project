from supervisely.app import DataJson, StateJson
from supervisely.app.widgets import ProjectSelector, ElementButton, SlyTqdm, DoneLabel, NotificationBox

import src.sly_globals as g

select_det_classes_button = ElementButton(text='SELECT 0 CLASSES', button_type='primary')
# select_det_classes_button.disabled = True
reselect_det_classes_button = ElementButton(text='<i style="margin-right: 5px" class="zmdi zmdi-rotate-left"></i>reselect', button_type='warning', button_size='small', plain=True)
det_classes_done_label = DoneLabel(text='')
det_classes_notification_box = NotificationBox(description='Choose classes that should be kept after prediction, other classes will be ignored', box_type='info')
