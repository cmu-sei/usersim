import json

import tasks


def construct_task(task_config):
    pass

def parse_config_string(config_string):
    try:
        config_obj = json.loads(config_string)
    except Exception:
        pass
