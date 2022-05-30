import supervisely as sly
from supervisely.app.fastapi import run_sync
import os
import cv2
import math

import src.sly_globals as g


def check_sliding_sizes_by_image(state, img_info):
    if state["windowHeight"] > img_info.height:
        state["windowHeight"] = img_info.height

    if state["windowWidth"] > img_info.width:
        state["windowWidth"] = img_info.width

    run_sync(state.synchronize_changes())
    

def refresh_progress_preview(state, progress: sly.Progress):
    state["progressPreview"] = int(progress.current * 100 / progress.total)
    state["progressPreviewMessage"] = progress.message
    state["progressPreviewCurrent"] = progress.current
    state["progressPreviewTotal"] = progress.total
    
    run_sync(state.synchronize_changes())


def write_video(state, img, predictions, last_two_frames_copies = 8, max_video_size = 1080):
    scale_ratio = None
    if img.shape[1] > max_video_size:
        scale_ratio = max_video_size / img.shape[1]
        img = cv2.resize(img, (int(img.shape[1] * scale_ratio), int(img.shape[0] * scale_ratio)))

    video_path = os.path.join(g.app_data_dir, "preview.mp4")
    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'VP90'), state["fps"], (img.shape[1], img.shape[0]))
    report_every = max(5, math.ceil(len(predictions) / 100))
    progress = sly.Progress("Rendering frames", len(predictions))
    refresh_progress_preview(state, progress)

    for i, pred in enumerate(predictions):
        rect = pred["rectangle"]
        rect = sly.Rectangle.from_json(rect)
        if scale_ratio is not None:
            rect = rect.scale(scale_ratio)
        labels = pred["labels"]
        for label_ind, label in enumerate(labels):
            labels[label_ind] = sly.Label.from_json(label, g.det_model_data["model_meta"])
        
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
        
        progress.iter_done_report()
        if i % report_every == 0:
            refresh_progress_preview(state, progress)

    progress = sly.Progress("Saving video file", 1)
    progress.iter_done_report()
    refresh_progress_preview(state, progress)
    video.release()

    progress = sly.Progress("Uploading video", 1)
    progress.iter_done_report()
    refresh_progress_preview(state, progress)
    remote_video_path = os.path.join(f"/apply_det_and_cls_to_project", "preview.mp4")
    if g.api.file.exists(g.TEAM_ID, remote_video_path):
        g.api.file.remove(g.TEAM_ID, remote_video_path)
    file_info = g.api.file.upload(g.TEAM_ID, video_path, remote_video_path)
    return file_info