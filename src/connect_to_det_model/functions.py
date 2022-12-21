import supervisely as sly
import src.sly_globals as g
import src.sly_functions as global_functions


def connect_to_model(state):
    model_task_id = state['det_model_id']
    if model_task_id is None:
        raise ValueError('det_model_id must be a number')
    g.det_model_data['info'] = global_functions.validate_response_errors(
        g.api.task.send_request(
            model_task_id, 
            "get_session_info",  
            data={},
            timeout=g.model_connection_timeout
        )
    )
    sly.logger.info("Model info", extra=g.det_model_data['info'])
    model_meta_json = global_functions.validate_response_errors(
            g.api.task.send_request(
                model_task_id, 
                "get_output_classes_and_tags", 
                data={}, 
                timeout=g.model_connection_timeout
            )
        )

    sly.logger.info(f"Model meta: {str(model_meta_json)}")
    g.det_model_data['model_meta'] = sly.ProjectMeta.from_json(model_meta_json)
