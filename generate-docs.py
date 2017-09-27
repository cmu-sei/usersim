import os
import subprocess

import api

tasks = api.get_tasks()

dynamic_document = '\\chapter{Task Parameters}\n\n'

def itemize(parameter_dict):
    dynamic_document = ''

    dynamic_document += '\\begin{itemize}\n'
    for item in sorted(parameter_dict):
        description = parameter_dict[item].rsplit(':', 1)[-1]
        dynamic_document += '\\item {}: {}\n'.format(item.replace('_', '\\_'), description.replace('_', '\\_'))
    dynamic_document += '\\end{itemize}\n'

    return dynamic_document

for task in sorted(tasks):
    parameters = tasks[task]
    try:
        required = parameters['required']
    except KeyError:
        required = {}
    try:
        optional = parameters['optional']
    except KeyError:
        optional = {}

    dynamic_document += '\\subsection{{{}}}\n\n'.format(task)

    if required:
        dynamic_document += '\\subsubsection{{Required Parameters}}\n\n'
        dynamic_document += itemize(required)

    if optional:
        dynamic_document += '\\subsubsection{{Optional Parameters}}\n\n'
        dynamic_document += itemize(optional)

print(dynamic_document)
