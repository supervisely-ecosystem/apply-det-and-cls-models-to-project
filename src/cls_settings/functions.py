import functools
import os
import random
import time

import cv2
import numpy as np

import src.det_settings.functions as det_settings_functions
import src.sly_functions as f
import src.sly_globals as g
import supervisely as sly
from supervisely.app import DataJson

import src.cls_settings.widgets as card_widgets


def selected_classes_event(state):
    g.selected_det_for_cls_classes = []
    for idx, class_name in enumerate(g.selected_det_classes):
        if state["selectedClasses"][idx]:
            g.selected_det_for_cls_classes.append(class_name)
    classes_len = len(g.selected_det_classes)
    # TODO: disable preview button if classes_len == 0


def get_objects_num_by_classes(selected_classes):
    total = 0
    for row in DataJson()['classes_table_content']:
        if row['name'] in selected_classes:
            total += row['obj_num']
    return total


def get_classes_table_content():
    table_data = []
    for class_obj in g.det_model_data['model_meta'].obj_classes.to_json():
        if class_obj["title"] in g.selected_det_classes:
            table_data.append({
                'name': class_obj["title"],
                'color': class_obj["color"],
                'shape': class_obj["shape"],
            })

    return table_data


def get_data_to_inference(images_batch):
    data = {
        'images_ids': [],
        'rectangles': []
    }

    for row in images_batch:

        if len(row) == 2:  # labels
            image_info, label = row

            label_bbox = label.geometry.to_bbox()
            bbox = [
                label_bbox.top,
                label_bbox.left,
                label_bbox.bottom,
                label_bbox.right
            ]

            data['rectangles'].append(bbox)

        else:  # only images
            image_info = row

        data['images_ids'].append(image_info.id)

    if len(data['rectangles']) == 0:  # remove rectangles if doesn't exist
        data.pop('rectangles')

    return data


def get_tags_list_for_predictions(predictions_row):

    pred_scores_list, pred_classes_list = predictions_row['score'], predictions_row['class']

    tags_list = []
    for name, value in zip(pred_classes_list, pred_scores_list):
        tag_meta = g.output_project_meta.get_tag_meta(f'{name}{g.cls_model_tag_suffix}')

        if tag_meta.value_type == sly.TagValueType.NONE:
            tags_list.append(sly.Tag(meta=tag_meta))
        else:
            tags_list.append(sly.Tag(meta=tag_meta, value=value))

    return tags_list


def add_predicted_tags_to_labels(labels_batch, predictions):
    updated_labels = []

    for index, row in enumerate(labels_batch):
        label: sly.Label = row[1]

        if predictions[index] is None:
            sly.logger.warning(f'cannot read prediction for label {row}')
            continue

        tags_list = get_tags_list_for_predictions(predictions[index])

        updated_labels.append(label.clone(tags=sly.TagCollection(tags_list)))

    return updated_labels


def get_predicted_tags_for_images(labels_batch, predictions):
    predicted_tags_collections = []

    for index, row in enumerate(labels_batch):

        if predictions[index] is None:
            sly.logger.warning(f'cannot read prediction for label {row}')
            continue

        tags_list = get_tags_list_for_predictions(predictions[index])
        predicted_tags_collections.append(sly.TagCollection(tags_list))

    return predicted_tags_collections


def get_predicted_labels_for_batch(labels_batch, model_session_id, top_n, padding):
    inference_data = get_data_to_inference(labels_batch)
    predictions = g.api.task.send_request(model_session_id, "inference_batch_ids", data={
        'topn': top_n,
        'pad': padding,
        **inference_data
    })

    if len(labels_batch[0]) == 2:  # labels
        return add_predicted_tags_to_labels(labels_batch, predictions)
    else:  # images
        return get_predicted_tags_for_images(labels_batch, predictions)


def update_project_items_by_predicted_labels(labels_batch, predicted_labels):
    dsid2dataset = f.get_datasets_dict_by_project_dir(g.output_project_dir)

    for index, predicted_label in enumerate(predicted_labels):

        if len(labels_batch[index]) == 2:  # labels
            item_info, det_label = labels_batch[index]
            dataset: sly.Dataset = dsid2dataset[item_info.dataset_id]

            if item_info.id in g.updated_images_ids:
                ann = dataset.get_ann(item_info.name, project_meta=g.output_project.meta)
            else:
                ann = sly.Annotation(img_size=(item_info.height, item_info.width))
            ann_labels = ann.labels
            det_and_cls_label = det_label.add_tags(predicted_label.tags)
            ann_labels.append(det_and_cls_label)
            updated_ann = ann.clone(labels=ann_labels)

        else:  # images
            item_info = labels_batch[index]
            dataset: sly.Dataset = dsid2dataset[item_info.dataset_id]
            if item_info.id in g.updated_images_ids:
                updated_ann = dataset.get_ann(item_info.name, project_meta=g.output_project.meta)
                updated_ann = updated_ann.add_tags(predicted_label)
            else:
                updated_ann = sly.Annotation(img_size=(item_info.height, item_info.width), img_tags=predicted_label)

        dataset.set_ann(item_name=item_info.name, ann=updated_ann)

        if item_info.id not in g.updated_images_ids:
            g.updated_images_ids.add(item_info.id)


def update_annotations_in_for_loop(state):
    selected_classes_list = g.selected_det_for_cls_classes if state['selectedLabelingMode'] == "Objects" else None

    with card_widgets.labeling_progress(message='applying models to project data', total=len(g.images_info)) as pbar:
        for image_info in g.images_info:

            det_settings_functions.check_sliding_sizes_by_image(state, image_info)
            inf_settings = {
                "conf_thres": state["conf_thres"],
                "iou_thres": state["iou_thres"],
                "inference_mode": state["inference_mode"]
            }
            if state["inference_mode"] == "sliding_window":
                inf_settings["sliding_window_params"] = {
                    "windowHeight": state["windowHeight"],
                    "windowWidth": state["windowWidth"],
                    "overlapY": state["overlapY"],
                    "overlapX": state["overlapX"],
                    "borderStrategy": state["borderStrategy"]
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
                det_ann = ann_pred_res["annotation"]
            else:
                det_ann = ann_pred_res
            det_ann = sly.Annotation.from_json(det_ann, g.output_project_meta)
            det_labels = det_ann.labels

            # add detection labels of classes NOT for classification model
            dsid2dataset = f.get_datasets_dict_by_project_dir(g.output_project_dir)
            dataset: sly.Dataset = dsid2dataset[image_info.dataset_id]

            labels_to_append = []
            for label in det_labels:
                if selected_classes_list is None or label.obj_class.name not in selected_classes_list:
                    labels_to_append.append(label)

            if image_info.id in g.updated_images_ids:
                ann = dataset.get_ann(image_info.name, project_meta=g.output_project.meta)
            else:
                ann = sly.Annotation(img_size=(image_info.height, image_info.width))
            updated_ann = ann.add_labels(labels_to_append)
            dataset.set_ann(item_name=image_info.name, ann=updated_ann)
            if image_info.id not in g.updated_images_ids:
                g.updated_images_ids.add(image_info.id)

            # add combined det + cls labels of classes for classification model
            labels_batch = []

            for label_info_to_annotate in f.get_images_to_label(image_info, selected_classes_list, det_labels):
                labels_batch.append(label_info_to_annotate)

                if len(labels_batch) == g.batch_size:
                    predicted_labels = get_predicted_labels_for_batch(
                        labels_batch=labels_batch,
                        model_session_id=state['cls_model_id'],
                        top_n=state['topN'],
                        padding=state['padding']
                    )
                    update_project_items_by_predicted_labels(labels_batch, predicted_labels)
                    labels_batch = []

            if len(labels_batch) != 0:
                predicted_labels = get_predicted_labels_for_batch(
                    labels_batch=labels_batch,
                    model_session_id=state['cls_model_id'],
                    top_n=state['topN'],
                    padding=state['padding']
                )
                update_project_items_by_predicted_labels(labels_batch, predicted_labels)
            
            pbar.update()


def label_project(state):
    f.create_output_project(input_project_dir=g.project_dir, output_project_dir=g.output_project_dir)
    f.update_project_tags_by_model_meta(project_dir=g.output_project_dir, state=state)

    g.output_project = sly.Project(g.output_project_dir, mode=sly.OpenMode.READ)
    g.output_project_meta = sly.Project(g.output_project_dir, mode=sly.OpenMode.READ).meta

    update_annotations_in_for_loop(state=state)


def upload_project(state):
    output_project_name = state["outputProject"]

    with card_widgets.labeling_progress(message='uploading project', total=g.output_project.total_items * 2) as pbar:
        project_id, project_name = sly.upload_project(dir=g.output_project_dir, api=g.api,
                                                      project_name=output_project_name,
                                                      workspace_id=g.WORKSPACE_ID, progress_cb=pbar.update)

        project_info = g.api.project.get_info_by_id(project_id)
        DataJson()['outputProject'] = {
            'id': project_info.id,
            'name': project_name,
            'img_url': project_info.reference_image_url,
        }


def stringify_label_tags(predicted_tags):
    final_message = ''

    for index, tag in enumerate(predicted_tags):
        value = ''
        if tag.value is not None:
            value = f":{round(tag.value, 3)}"

        final_message += f'top@{index + 1} — {tag.name}{value}<br>'

    return final_message


@functools.lru_cache(maxsize=10)
def get_image_by_id(image_id):
    return cv2.cvtColor(g.api.image.download_np(image_id), cv2.COLOR_BGR2RGB)


def get_bbox_with_padding(rectangle, pad_percent, img_size):
    top, left, bottom, right = rectangle
    height, width = img_size

    if pad_percent > 0:
        sly.logger.debug("before padding", extra={"top": top, "left": left, "right": right, "bottom": bottom})
        pad_lr = int((right - left) / 100 * pad_percent)
        pad_ud = int((bottom - top) / 100 * pad_percent)
        top = max(0, top - pad_ud)
        bottom = min(height - 1, bottom + pad_ud)
        left = max(0, left - pad_lr)
        right = min(width - 1, right + pad_lr)
        sly.logger.debug("after padding", extra={"top": top, "left": left, "right": right, "bottom": bottom})

    return [top, left, bottom, right]


def clean_up_preview_images_dir():
    preview_files_path = os.path.join('static', 'preview_images')
    static_files_dir = os.path.join(g.app_root_directory, preview_files_path)
    os.makedirs(static_files_dir, exist_ok=True)
    sly.fs.clean_dir(static_files_dir)


def get_cropped_image_url(label_b, state):
    img_info, label = label_b
    img_np = get_image_by_id(img_info.id)

    try:
        sly_rectangle = label.geometry.to_bbox()
        rectangle = [
            sly_rectangle.top,
            sly_rectangle.left,
            sly_rectangle.bottom,
            sly_rectangle.right
        ]

        top, left, bottom, right = get_bbox_with_padding(rectangle=rectangle, pad_percent=state['padding'],
                                                         img_size=img_np.shape[:2])

        rect = sly.Rectangle(top, left, bottom, right)
        cropping_rect = rect.crop(sly.Rectangle.from_size(img_np.shape[:2]))[0]
        img_np = sly.image.crop(img_np, cropping_rect)

    except Exception as ex:
        sly.logger.warning(f'Cannot crop image: {ex}')

    if np.prod(img_np.shape[:2]) > 1:
        preview_files_path = os.path.join('static', 'preview_images')
        static_files_dir = os.path.join(g.app_root_directory, preview_files_path)

        filename = f'{img_info.id}_{time.time_ns()}.png'
        image_path = os.path.join(static_files_dir, filename)
        cv2.imwrite(image_path, img_np)

        return os.path.join(preview_files_path, filename)


def get_images_for_preview(state, img_num):
    clean_up_preview_images_dir()

    g.output_project_meta = f.get_project_meta_merged_with_model_tags(g.project_dir, state)

    selected_classes_list = g.selected_det_for_cls_classes if state['selectedLabelingMode'] == "Objects" else None
    labels_batch = []
    for label_info_to_annotate in f.get_images_to_label(g.preview_image, selected_classes_list, g.preview_boxes):
        labels_batch.append(label_info_to_annotate)
        if len(labels_batch) == img_num * 5:
            break

    random.shuffle(labels_batch)
    labels_batch = labels_batch[:img_num]

    predicted_labels = get_predicted_labels_for_batch(
        labels_batch=labels_batch,
        model_session_id=state['cls_model_id'],
        top_n=state['topN'],
        padding=state['padding']
    )

    images_for_preview = []
    for label_b, predicted_label in zip(labels_batch, predicted_labels):
        img_url = get_cropped_image_url(label_b, state) if len(label_b) == 2 else label_b.path_original
        if img_url is None:
            continue

        images_for_preview.append({
            'url': get_cropped_image_url(label_b, state) if len(label_b) == 2 else label_b.path_original,
            'title': stringify_label_tags(predicted_label.tags) if len(label_b) == 2 else stringify_label_tags(predicted_label)
        })

    return images_for_preview