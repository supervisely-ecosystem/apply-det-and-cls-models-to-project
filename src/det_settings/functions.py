import supervisely as sly
from supervisely.app.fastapi import run_sync
import os
import cv2
import math
import random
import copy

import src.sly_globals as g
import src.sly_functions as f
import src.det_settings.widgets as card_widgets


def get_images_for_preview_list():
    images_for_preview_list = []
    for image_info in g.images_info:
        images_for_preview_list.append({
            'label': image_info.name,
            'value': image_info.id,
        })
    return images_for_preview_list


def check_sliding_sizes_by_image(state, img_info):
    if state["windowHeight"] > img_info.height:
        state["windowHeight"] = img_info.height

    if state["windowWidth"] > img_info.width:
        state["windowWidth"] = img_info.width

    run_sync(state.synchronize_changes())


def write_video(state, img, predictions, last_two_frames_copies = 8, max_video_size = 1080):
    scale_ratio = None
    if img.shape[1] > max_video_size:
        scale_ratio = max_video_size / img.shape[1]
        img = cv2.resize(img, (int(img.shape[1] * scale_ratio), int(img.shape[0] * scale_ratio)))

    video_path = os.path.join(g.app_data_dir, "preview.mp4")
    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'VP90'), state["fps"], (img.shape[1], img.shape[0]))

    with card_widgets.det_preview_progress(message='Rendering frames...', total=len(predictions)) as pbar:
        for i, pred in enumerate(predictions):
            rect = pred["rectangle"]
            rect = sly.Rectangle.from_json(rect)
            if scale_ratio is not None:
                rect = rect.scale(scale_ratio)
            labels = []
            for label_json in pred["labels"]:
                label = sly.Label.from_json(label_json, g.det_model_data["model_meta"])
                if label.obj_class.name in g.selected_det_classes:
                    labels.append(label)
            
            frame = img.copy()
            rect.draw_contour(frame, [255, 0, 0], thickness=5)
            for label in labels:
                if scale_ratio is not None:
                    label = sly.Label(label.geometry.scale(scale_ratio), label.obj_class)
                label.draw_contour(frame, thickness=3)
            sly.image.write(os.path.join(g.app_data_dir, f"{i:05d}.jpg"), frame)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if i >= len(predictions) - 2:
                for n in range(last_two_frames_copies):
                    video.write(frame_bgr)
            else:
                video.write(frame_bgr)
            
            pbar.update()

    with card_widgets.det_preview_progress(message='Saving video file...', total=1) as pbar:
        video.release()
        pbar.update()

    with card_widgets.det_preview_progress(message='Uploading video...', total=1) as pbar:
        remote_video_path = os.path.join(f"/apply_det_and_cls_to_project", "preview.mp4")
        if g.api.file.exists(g.TEAM_ID, remote_video_path):
            g.api.file.remove(g.TEAM_ID, remote_video_path)
        file_info = g.api.file.upload(g.TEAM_ID, video_path, remote_video_path)
        pbar.update()
    return file_info


def get_preview_predictions(state):
    if state['randomImagePreview'] is True:
        image_info = random.choice(g.images_info)
    else:
        image_info = [image_info for image_info in g.images_info if image_info.id == state['previewOnImageId']][0]

    check_sliding_sizes_by_image(state, image_info)
    inf_settings = {
        "conf_thres": state["conf_thres"],
        "iou_thres": state["iou_thres"],
        "inference_mode": state["inference_mode"],
        "sliding_window_params": {
            "windowHeight": state["windowHeight"],
            "windowWidth": state["windowWidth"],
            "overlapY": state["overlapY"],
            "overlapX": state["overlapX"],
            "borderStrategy": state["borderStrategy"]
        }
    }
    ann_pred_res = f.validate_response_errors(
        g.api.task.send_request(
            state['det_model_id'], 
            "inference_image_id",
            data={
                "image_id": image_info.id,
                "settings": inf_settings
            }, 
            timeout=g.model_inference_timeout
        )
    )
    if isinstance(ann_pred_res, dict) and "data" in ann_pred_res.keys():
        predictions = ann_pred_res["data"]["slides"]
    else:
        raise ValueError("Selected detection model doesn't support sliding window mode!")
    g.preview_image = image_info
    g.preview_boxes = []
    
    labels = copy.deepcopy(predictions[-1]["labels"]) # final boxes after NMS

    for label_json in labels:
        label = sly.Label.from_json(label_json, g.det_model_data["model_meta"])
        if label.obj_class.name in g.selected_det_classes:
            g.preview_boxes.append(label) 
    return image_info, predictions