import os
import subprocess

import api


# Shamelessly ripped from PyLaTeX utils.py, edited May 8, MIT License.
_latex_special_chars = {'&': r'\&',
                        '%': r'\%',
                        '$': r'\$',
                        '#': r'\#',
                        '_': r'\_',
                        '{': r'\{',
                        '}': r'\}',
                        '~': r'\textasciitilde{}',
                        '^': r'\^{}',
                        '\\': r'\textbackslash{}',
                        '\n': '\\newline%\n',
                        '-': r'{-}',
                        '\xA0': '~',  # Non-breaking space
                        '[': r'{[}',
                        ']': r'{]}',
}

# Shamelessly ripped from PyLaTeX utils.py, edited May 8, MIT License.
def escape_latex(s):
    """ Escape a string for use in a LaTeX document.

    Args:
        s (str): The string to escape.

    Returns:
        str: A string with its characters escaped for use in a LaTeX document.
    """
    return ''.join(_latex_special_chars.get(c, c) for c in s)

tasks = api.get_tasks()

dynamic_document = '\\chapter{Task Parameters}\n\n'

def itemize(parameter_dict):
    dynamic_document = ''

    dynamic_document += '\\begin{itemize}\n'
    for item in sorted(parameter_dict):
        description = parameter_dict[item].rsplit(':', 1)[-1]
        dynamic_document += '\\item {}: {}\n'.format(escape_latex(item), escape_latex(description))
    dynamic_document += '\\end{itemize}\n'

    return dynamic_document

for task in sorted(tasks):
    parameters = tasks[task]
    description = parameters['description']
    try:
        required = parameters['required']
    except KeyError:
        required = {}
    try:
        optional = parameters['optional']
    except KeyError:
        optional = {}

    dynamic_document += '\\subsection{{{}}}\n\n'.format(task)

    dynamic_document += escape_latex(description) + '\n\n'

    if required:
        dynamic_document += '\\subsubsection{{Required Parameters}}\n\n'
        dynamic_document += itemize(required)

    if optional:
        dynamic_document += '\\subsubsection{{Optional Parameters}}\n\n'
        dynamic_document += itemize(optional)

cwd = os.getcwd()
os.chdir('docs/latex/')
print(os.listdir())
with open('dynamic.tex', 'w') as f:
    f.write(dynamic_document)

subprocess.run(['latexmk', '-pdf', 'developer-guide.tex'], check=True, timeout=60)
subprocess.run(['latexmk', '-pdf', 'user-guide.tex'], check=True, timeout=60)
subprocess.run(['latexmk', '-c'], check=True, timeout=60)
