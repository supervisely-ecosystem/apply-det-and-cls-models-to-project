from supervisely.app import DataJson, StateJson
from supervisely.app.widgets import ProjectSelector, ElementButton, SlyTqdm, DoneLabel, NotificationBox

import src.sly_globals as g

connect_det_model_button = ElementButton(text='CONNECT', button_type='primary')
reselect_det_model_button = ElementButton(text='<i style="margin-right: 5px" class="zmdi zmdi-rotate-left"></i>reselect', button_type='warning', button_size='small', plain=True)
connect_det_model_notification_box = NotificationBox(description='Select served Detection Model from list below', box_type='info')
