from supervisely.app import DataJson, StateJson
from supervisely.app.widgets import ProjectSelector, ElementButton, SlyTqdm, DoneLabel, NotificationBox

import src.sly_globals as g

select_all_det_classes_button = ElementButton(text='<i class="zmdi zmdi-check-all"></i> SELECT ALL', button_type='text', button_size='mini', plain=True)
deselect_all_det_classes_button = ElementButton(text='<i class="zmdi zmdi-square-o"></i> DESELECT ALL', button_type='text', button_size='mini', plain=True)
select_det_classes_button = ElementButton(text='SELECT 0 CLASSES', button_type='primary')
select_det_classes_button.disabled = True
reselect_det_classes_button = ElementButton(text='<i style="margin-right: 5px" class="zmdi zmdi-rotate-left"></i>select other classes', button_type='warning', button_size='small', plain=True)
det_classes_done_label = DoneLabel(text='')