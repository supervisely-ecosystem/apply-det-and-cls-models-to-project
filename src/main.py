from fastapi import Request, Depends

import src.sly_globals as g

import src.input_project
import src.connect_to_det_model
import src.det_classes
import src.det_settings
import src.connect_to_cls_model
import src.cls_settings

from supervisely.app.fastapi import available_after_shutdown

@g.app.get("/")
@available_after_shutdown(app=g.app)
def read_index(request: Request):
    return g.templates_env.TemplateResponse('index.html', {'request': request})



@g.app.on_event("shutdown")
def shutdown():
    read_index()  # save last version of static files
