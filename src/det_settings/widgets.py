from supervisely.app import DataJson, StateJson
from supervisely.app.widgets import ProjectSelector, ElementButton, SlyTqdm, DoneLabel, NotificationBox

import src.sly_globals as g

select_det_settings_button = ElementButton(text='SAVE SETTINGS', button_type='primary')
show_det_preview_button = ElementButton(text='<i class="zmdi zmdi-slideshow" style="margin-right: 5px"></i> PREVIEW', button_type='primary')
reselect_det_settings_button = ElementButton(text='<i style="margin-right: 5px" class="zmdi zmdi-rotate-left"></i>Reselect settings', button_type='warning', button_size='small', plain=True)
det_settings_selected_done_label = DoneLabel(text='Detection settings saved')
