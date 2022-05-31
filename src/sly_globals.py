import os
from pathlib import Path

from fastapi import FastAPI
from supervisely.sly_logger import logger
from starlette.staticfiles import StaticFiles

import supervisely as sly
from supervisely.app import DataJson, StateJson
from supervisely.app.fastapi import create, Jinja2Templates
from dotenv import load_dotenv
from collections import OrderedDict

app_root_directory = str(Path(__file__).parent.absolute().parents[0])
logger.info(f"App root directory: {app_root_directory}")
app_data_dir = os.path.join(app_root_directory, 'tempfiles')
app_cache_dir = os.path.join(app_data_dir, 'cache')

# TODO: for debug
load_dotenv(os.path.join(app_root_directory, "debug.env"))
load_dotenv(os.path.join(app_root_directory, "secret_debug.env"), override=True)

api = sly.Api.from_env()
file_cache = sly.FileCache(name="FileCache", storage_root=app_cache_dir)
app = FastAPI()
sly_app = create()

TEAM_ID = int(os.getenv('context.teamId'))
WORKSPACE_ID = int(os.getenv('context.workspaceId'))
PROJECT_ID = int(os.getenv('modal.state.slyProjectId')) if os.getenv('modal.state.slyProjectId').isnumeric() else None

app.mount("/sly", sly_app)
app.mount("/static", StaticFiles(directory=os.path.join(app_root_directory, 'static')), name="static")
templates_env = Jinja2Templates(directory=os.path.join(app_root_directory, 'templates'))

project_dir = os.path.join(app_data_dir, 'project_dir')

output_project_dir = os.path.join(app_data_dir, 'output_project_dir')
output_project: sly.Project = None
output_project_meta: sly.ProjectMeta = None
model_connection_timeout = 500
model_inference_timeout = 1000

project = {
    'workspace_id': None,
    'project_id': None,
    'dataset_ids': []
}
images_info = []
updated_images_ids = set()
preview_image = None
preview_boxes = None
selected_det_classes = []
selected_det_for_cls_classes = []
batch_size = 64

det_model_data = {}
cls_model_data = {}
cls_model_tag_suffix = ''

DataJson()['steps'] = OrderedDict({
    "input_project": 1,
    "connect_to_det_model": 2,
    "det_classes": 3,
    "det_settings": 4,
    "connect_to_cls_model": 5,
    "cls_settings": 6,
    "output_data": 7
})
DataJson()['current_step'] = 1
DataJson()['team_id'] = TEAM_ID
DataJson()['workspace_id'] = WORKSPACE_ID
DataJson()['instanceAddress'] = os.getenv('SERVER_ADDRESS')
StateJson()['collapsed_steps'] = {
    "input_project": False,
    "connect_to_det_model": True,
    "det_classes": True,
    "det_settings": True,
    "connect_to_cls_model": True,
    "cls_settings": True,
    "output_data": True
}
