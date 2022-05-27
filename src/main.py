from fastapi import Request, Depends

import src.sly_globals as g

import src.input_project
import src.connect_to_det_model
import src.det_classes
import src.det_inference_mode


@g.app.get("/")
def read_index(request: Request):
    return g.templates_env.TemplateResponse('index.html', {'request': request})

