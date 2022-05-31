import os
import supervisely as sly

import src.sly_globals as g

def validate_response_errors(data):
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def get_images_to_label(project_dir, selected_classes_names=None, predicted_labels=None, image_info=None) -> dict:
    if selected_classes_names is not None:
        for label in predicted_labels:
            if label.obj_class.name in selected_classes_names:
                yield tuple([image_info, label])
    else:
        project = sly.Project(directory=project_dir, mode=sly.OpenMode.READ)
        for dataset in project.datasets:
            items_names = dataset.get_items_names()

            for item_name in items_names:
                image_info = dataset.get_image_info(item_name=item_name)

                yield image_info

def create_output_project(input_project_dir, output_project_dir):
    os.makedirs(output_project_dir, exist_ok=True)
    sly.fs.clean_dir(output_project_dir)
    sly.Project(directory=input_project_dir, mode=sly.OpenMode.READ).copy_data(
        dst_directory=g.app_data_dir, dst_name='output_project_dir')


def get_model_tags_list(model_tags_metas, suffix_value=None, suffix_needed=False, add_confidence=True):
    if suffix_value is None or suffix_value == '':
        suffix_value = '_nn'

    tags_metas_list = []
    for tag_meta in model_tags_metas:
        tag_name = tag_meta.name

        if suffix_needed is True:
            tag_name = f'{tag_name}{suffix_value}'

        tag_type = sly.TagValueType.ANY_NUMBER if add_confidence is True else sly.TagValueType.NONE
        tags_metas_list.append(sly.TagMeta(name=f'{tag_name}', value_type=tag_type))

    if suffix_needed:  # for reading in future
        g.cls_model_tag_suffix += suffix_value

    return tags_metas_list


def collisions_between_tags_exists(tag_metas, model_tags_metas):
    project_tags = {tag.name: tag.value_type for tag in tag_metas}
    model_tags = {tag.name: tag.value_type for tag in model_tags_metas}

    intersected_tag_names = set(project_tags.keys()).intersection(set(model_tags.keys()))

    for tag_name in intersected_tag_names:
        if project_tags[tag_name] != model_tags[tag_name]:
            return True
    return False


def get_project_meta_merged_with_model_tags(project_dir, state):
    model_meta: sly.ProjectMeta = g.cls_model_data['model_meta']

    model_tags_metas = get_model_tags_list(
        model_tags_metas=model_meta.tag_metas,
        suffix_value=state['suffixValue'],
        suffix_needed=state['addSuffix'],
        add_confidence=state['addConfidence']
    )

    project = sly.Project(project_dir, mode=sly.OpenMode.READ)
    # add detection classes
    meta_with_det = project.meta.merge(g.det_model_data["model_meta"])
    project.set_meta(meta_with_det)

    while collisions_between_tags_exists(project.meta.tag_metas, model_tags_metas):
        model_tags_metas = get_model_tags_list(
            model_tags_metas=model_tags_metas,
            suffix_value=state['suffixValue'],
            suffix_needed=True,
            add_confidence=state['addConfidence']
        )

    meta_with_model_labels = sly.ProjectMeta(tag_metas=sly.TagMetaCollection(model_tags_metas))
    return project.meta.merge(meta_with_model_labels)


def update_project_tags_by_model_meta(project_dir, state):
    merged_meta = get_project_meta_merged_with_model_tags(project_dir, state)
    project = sly.Project(project_dir, mode=sly.OpenMode.READ)
    project.set_meta(merged_meta)


def get_datasets_dict_by_project_dir(directory):
    project = sly.Project(directory=directory, mode=sly.OpenMode.READ)
    dsid2dataset = {}
    for key, value in zip(project.datasets.keys(), project.datasets.items()):
        dsid2dataset[g.api.dataset.get_info_by_name(parent_id=g.project['project_id'], name=key).id] = value
    return dsid2dataset