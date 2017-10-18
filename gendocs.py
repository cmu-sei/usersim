import inspect
import os
import subprocess

import api


def generate():
    """ Create the API reference and task parameters docs and deposit them in the docs/ directory named api-reference.md
    and tasks.md, respectively.
    """
    tasks = api.get_tasks()

    # Generate API reference.
    api_reference = ['# API Reference']

    api_functions = sorted(inspect.getmembers(api, inspect.isfunction), key=lambda x: x[0])

    for name, function in api_functions:
        api_reference.append('## ' + name)
        doc = function.__doc__.strip()
        if doc:
            api_reference.append(doc)

    with open('docs/api-reference.md', 'w') as f:
        f.write('\n\n'.join(api_reference))

    # Generate Task parameters document.
    tasks_doc = ['# Task Parameters']

    tasks = api.get_tasks()
    for task in sorted(tasks):
        tasks_doc.append('## ' + task)
        description = tasks[task]['description']
        required = tasks[task]['required']
        optional = tasks[task]['optional']

        tasks_doc.append('### Description')
        tasks_doc.append(description)

        parameter_list = []
        for key in sorted(required):
            # TODO: Find a way to guarantee separation of types and parameter description. This breaks if a ':' is in the
            # description.
            parameter_desc = required[key]
            parameter_list.append('* ' + key + ' - ' + parameter_desc)

        if parameter_list:
            tasks_doc.append('### Required\n' + '\n'.join(parameter_list))

        parameter_list = []
        for key in sorted(optional):
            # TODO: Same as above. Also make this into a function.
            parameter_desc = optional[key].rsplit(':', 1)[-1]
            parameter_list.append('* ' + key + ' - ' + parameter_desc)

        if parameter_list:
            tasks_doc.append('### Optional\n' + '\n'.join(parameter_list))

    with open('docs/tasks.md', 'w') as f:
        f.write('\n\n\n\n'.join(tasks_doc))

if __name__ == '__main__':
    generate()
