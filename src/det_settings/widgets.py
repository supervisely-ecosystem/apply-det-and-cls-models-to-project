from supervisely.app import DataJson, StateJson
from supervisely.app.widgets import ProjectSelector, ElementButton, SlyTqdm, DoneLabel, NotificationBox, GridGallery

import src.sly_globals as g

select_det_settings_button = ElementButton(text='SAVE SETTINGS', button_type='primary')
show_det_preview_button = ElementButton(text='<i class="zmdi zmdi-slideshow" style="margin-right: 5px"></i> PREVIEW', button_type='primary', button_size='small')
show_det_full_preview_button = ElementButton(text='<i class="zmdi zmdi-slideshow" style="margin-right: 5px"></i> PREVIEW', button_type='primary', button_size='small')
reselect_det_settings_button = ElementButton(text='<i style="margin-right: 5px" class="zmdi zmdi-rotate-left"></i>Reselect settings', button_type='warning', button_size='small', plain=True)
det_settings_selected_done_label = DoneLabel(text='Detection settings saved')
det_preview_progress = SlyTqdm()
sliding_window_preview_notification_box = NotificationBox(description=' \
    This video shows in detail how sliding window inference is applied to your data:<br /> \
    Step 1: for every sliding window model produces raw predictions (without any post processing).<br /> \
    Step 2: raw predictions for every sliding window are combined together.<br /> \
    Step 3: post processing is applied to the result of step 2. For example, for detection model it can be NMS algorithm, every model implements \
    this post processing itself, current app just visualizes model outputs.<br /> \
    Step 4: final predictions are visualized at the end of the video.', box_type='info')
preview_det_grid_gallery = GridGallery(columns_number=2, show_opacity_slider=False, sync_views=True)
sliding_window_not_available_infobox = NotificationBox(description='Selected detection model does not support sliding window inference mode.', box_type='warning')