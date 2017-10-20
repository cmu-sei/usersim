# Introduction

This guide is intended for a developer who is contributing code to the UserSim project. This especially includes anyone
wanting to create new tasks to be included in the main repository. Please read through the whole document before writing
a new `Task` subclass, because it could save you a lot of time.

The first (most often overlooked) chapter covers code style guidelines and requirements. All code will be reviewed
before being integrated into the `master` branch of the repository, and there are some important requirements
that need to be met before the code will be merged into `master`.


# Installation

In this chapter, we'll go over the installation procedure for the UserSim.

## Requirements

The officially supported version of Python we're using for this project is 3.5. Some earlier versions of Python 3 will
probably work fine, and newer versions will also probably work fine as well. Python 2.7 and earlier **will not**
work, and are not supported.

Additionally, if you are using a 32-bit version of Office, you may need a 32-bit Python interpreter in order to interact
with Office. You will also need Outlook Redemption installed in order to interact with Outlook - as a developer, you can 
get Redemption under a developer license for no charge from the official website which is
<http://www.dimastr.com/redemption/home.htm> as of this writing.

## Environment

You may have your Python interpreter installed in any manner you'd like. However, as a recommendation of good practice,
you may want to create a Virtual Environment specifically for your usersim development.

In Python 3.5, this may be achieved by the following command:
```
python3.5 -m venv usersim-venv
source usersim-venv/bin/activate
```

This allows you to install packages to this virtual environment, without installing to the global Python directory.

### Linux

On Linux, you may want to take a further step and build Python from source in order to make sure that any actions you
take do not step on the system Python installation. The full details of building Python from source are out of the scope
of this document, but when you run the `configure` script, you will want to run the following command instead:

```
./configure --enable-shared LDFLAGS=-Wl,-rpath,`pwd`
```

(The marks surrounding `pwd` are not single-quotes - they are the backtick character, which is the key to the
left of the `1` key on US keyboards.)

This will build a dynamically-linked Python interpreter and the Python shared library. The shared library is required by
PyInstaller. Then, when you create your virtual environment, you can use the interpreter that you compiled:

```
/path/to/my/python -m venv usersim-venv
source usersim-venv/bin/activate
```

## Python Dependencies

In the root of the UserSim source tree, there is a file `client-requirements.txt`. We can directly feed this
file into the `pip` command to let it install all of the Python packages we need:

```
pip install -r client-requirements.txt
```

or

```
python -m pip install -r client-requirements.txt
```

(For Windows, which does not include the `pip` command in the PATH by default.)

The command above is assuming that you are using a virtual environment. If you are not using a virtual environment, you
must make sure that you are using the right `pip` command. This is because commonly, especially on Linux 
distributions, Python 2.7 is installed alongside a version of Python 3, and in such cases the `pip` command 
usually installs packages for Python 2.7. You will need to consider this for your system. The bottom line is to make
sure that you're installing packages for the right Python version, or better yet, use a virtual environment.

### Windows

On Windows, you will additionally want to run
```
python -m pip install pypiwin32
```
in order to install the various Win32 API extensions, which are used extensively in controlling Office programs.

## Non-Python Dependencies

Generally, non-Python binary dependencies should already be packaged with the source tree. An exception of note is a 
Visual C++ redistributable. On Windows, you may need to install a version of the VC++ redistributable in order to get 
Python to work.

# Code Style

This chapter discusses the code style used in the UserSim project. In order to maintain consistency across the entire
codebase, new tasks should be written to adhere as closely as possible to the following guide.

In case your question is not addressed in this chapter or the linked web page, you may be able to find examples in other
portions of the project code to use in order to quickly get an answer, but you should email
<jvessella@cert.org> whether you find your answer or not. This will help to make this
document more complete.

## PEP-8

<https://www.python.org/dev/peps/pep-0008/>

For the most part, we will be attempting to adhere to PEP-8. This section will call out both the most important aspects
of PEP-8 that must be followed in order to contribute to the UserSim project, as well as some less important aspects
that PEP-8 does not specify, and are not critical to project code.

### Indentation
**The most important part of PEP-8 to follow is indentation.** All indented lines **must** be indented in
multiples of four spaces. Mixing tabs and spaces will inevitably lead to code mysteriously breaking without it being
apparent *why* it's breaking. Four spaces looks pretty consistent across text editors, and any worthwhile text
editor will allow you to modify the behavior of the Tab key to insert four spaces instead of a tab character.

### Naming Convention
The second most important part of PEP-8 is the naming convention. Top among any part of the naming convention is making
**descriptive** names for your variables. Obviously, you shouldn't need to write an entire sentence into a variable
name, but we're also not playing Wheel of Fortune here, either. Vowels are free, and you should generally type out the
full word. Naturally, some words are obnoxiously long, and for these you should use your judgment whether to shorten
them or not. Most variables will be single words, but it is acceptable to have a two to three word variable, where each
word is separated by an underscore.

While specified in PEP-8, it's worth mentioning that the project is also following the rest of the naming conventions as
well. This means that variables, methods, and functions will use the `lower_case_with_underscores` style,
while classes use the `CapitalizedWords` style.

### String Quoting
Since PEP-8 doesn't make a recommendation for single vs. double quotes, it's worth mentioning here that the project
mostly uses single quotes to express string literals. This is not too important to follow, but it's nice to have
consistency across the whole project. In cases where a string must contain single quotes, it's recommended to use
double quotes for the literal instead of using backslashes to escape the contained quotes.

### Comments
Sometimes, you will have to do things you are not proud of in order to get your code to work. In these situations, it is
*imperative* that you add a comment explaining why your code is doing something that looks out of place. For
example, suppose you are using a library function that will only write to a file-like object, but you actually want to 
use its output in your code. In order to work around this limitation, you might want to use an io.BytesIO object, like 
the following:

```
def get_string(obj):
    with io.BytesIO() as f:
        obj.write(f)
        return f.getvalue()
```

then you should have a comment explaining why you need to use a workaround, like so:

```
def get_string(obj):
    # obj does not have a tostring method, so we use io.BytesIO to work around that
    # limitation.
    with io.BytesIO() as f:
        obj.write(f)
        return f.getvalue()
```

## Google Style Docstrings

<https://google.github.io/styleguide/pyguide.html#Comments>

The only time we will intentionally diverge from PEP-8 recommendations is in docstrings. This is in order to have a
well-defined structure to our docstrings, in the hope of making them as clear and consistent as possible. In fact, there
are a couple of minor modifications to the Google docstrings that you should know about...

### Args

When listing the arguments in a docstring, each argument should specify its **type** after the variable name, like
so:

```
def print_something(number, letters):
    """ Tries to print stuff with the number and letters.

    Args:
        number (int): A positive int.
        letters (str): A string consisting only of letters.
    """
```

Sometimes you will need to express types that are more complex, such as a list of strings. In such a case, you should
specify the top-level type after the variable name, and then give more detail about what is expected in the 
description of the variable, as in the following examples:

```
def print_list_sum(a_list):
    """ Print the sum of a list of numbers.

    Args:
        a_list (list): A list containing ints or floats.
    """
```

```
def print_example(a_dict):
    """ Prints the content of the 'Example' key.

    Args:
        a_dict (dict): A dict with the key 'Example'.
    """
```

Or, you may also choose to express compound types within the type specification, like so:

```
def print_list_sum(a_list):
    """ Print the sum of a list of ints.

    Args:
        a_list (list of int): A list containing ints.
    """
```

The most important takeaway is that you capture as precisely as possible how your function is to be called and express
it clearly.

### Returns

Just as in the Args section of a docstring, we specify the type of a return value. In this case, specify the return type
before the description, like so:

```
def fetch_joke():
    """ Fetch a joke.

    Returns:
        str: A bad joke.
    """
```

Also like in the Args section, complex return value types should specify the top-level type of the returned object, and
the description should clarify what it contains, like so:

```
def fetch_{}:
    """ Fetch a dict object with particular keys.

    Returns:
        dict: A dict whose keys are ints and whose values are strings.
    """
```

Similarly to Args, you may also express compound return types in the type specification:

```
def fetch_list_of_dicts():
    """ Fetch a list that contains dict objects.

    Returns:
        list of dict: A list that contains dict objects.
    """
```

Again, the most important part of this is making it clear what is being returned by this function as precisely as
possible.

### Raises

We do not modify the Google recommendation for the Raises section:

```
def check_os():
    """ Checks which OS you're on.

    Raises:
        OSError: If you're on Windows.
    """
```

# The Task Class

The `Task` class should be your go-to parent class for any task that you write, if you are not specifically
inheriting from another `Task` subclass. The full path to the class is `tasks.task.Task`, and you
will (obviously) need to import the `tasks.task` module in order to create a subclass.

The following methods are **required** to be implemented, but it is highly encouraged to make your code as modular
and clean as possible by breaking more complex behavior into separate methods.

## \_\_init\_\_

As with any Python class, the `__init__` method is your constructor. All `Task` subclasses have an
`__init__` method that takes a `config` argument. This argument is a config dictionary that is
guaranteed to have already been passed through your subclass' `validate` method. What you do with your config
dictionary is up to you.

This is generally where you will want to initialize long-running threads if your task is supposed to spawn any threads.

```
"""
Args:
    config (dict): A task dict that has been sanitized by the validate method.
"""
```

## \_\_call\_\_

`__call__` is known as a magic method. A class implementing this method becomes callable, but you don't really
need to worry about what that means in order to write a task. This method is called each time the UserSim cycles, until
the task is paused or stopped. This method should be the entry point for your task's behavior. It's recommended that if
your task has any complexity, you should break this complexity into additional methods.

## cleanup

This method is called when a task is stopped. Most task implementations will not actually need to do anything with their
`cleanup` method and can simply `pass`. However, a long-running task that is eventually stopped
should probably clean up any threads it started or quit any external application that it's interacting with in this
method.

## stop

This method is called in each cycle to check whether the task *should* stop. Most tasks will simply define this
method to return `True` in order that the task will only be executed once, but a long-running task may want
to check if some internal state has been reached before stopping.

```
"""
Returns:
    bool: True if the task should stop, False if it should continue.
"""
```

## status

This method is called whenever the task's status is polled. This is intended as a way to report the current status of a
running task to a **human**, not a machine. The return should be a human-readable string. One-shot tasks can get
away with returning an empty string, but long-running tasks should usually give some kind of feedback about what is
going on internally.

```
"""
Returns:
    str: A human-readable string indicating the current status of this task.
"""
```

## parameters

**This is a class method.**

This method returns what amounts to a specification for the task's config dictionary. The intention was to have a
dictionary with two keys, 'required' and 'optional', each with dictionaries holding the required and optional keys,
respectively, and their human-readable description. Your description string should be prefixed with
a type specification, followed by a ':' (colon) character. For example:

```
required = {'a_number': 'int: A number to use, for reasons.'}
```

To be more specific, this type specification is YAML format. It's best to use compact YAML, however. Specifically, if
one of your keys takes a list of strings, your type specification would simply be:

```
'somekey': '[str]: Describe what this key is for and any additional constraints.'
```

A dict whose keys are ints and whose values are bools would be as follows:

```
'anotherkey': '{int: bool}: Describe what this dict is used for and any additional'
    ' constraints on it.'
```

The following basic types can be represented in the type specification: `bool`, `int`, 
`float`, `str`. You may also specify `any` to allow any of these types to be accepted, or
`number` to allow for the input to be an int or a float. Finally, you may specify `task` if you want 
to specify that a task configuration is expected.

```
"""
Returns:
    dict: A dictionary with keys 'required' and 'optional', and whose values are
        dictionaries respectively containing the required and optional parameters
        of the class as keys and human-readable (str) descriptions of those inputs
        as values.
"""
```

## validate

**This is a class method.**

This method takes a task dictionary and validates it. If the dictionary is invalid in some way, it should raise an
exception (detailed below). Note that the input dictionary is **not** the same as the dictionary returned by
`parameters`. **It does not separate keys into sub-dictionaries under 'required' and 'optional' keys.**
This dictionary mixes required and optional parameters, and you will need to validate those inputs in this method.

You may expect Python primitives, such as `bool`, `int`, `float`, or `str`.
types. `list` and `dict` are also allowed.

You may call the API function `check_config` to handle basic type-checking for the user-supplied config and to
add any missing optionals in one call. However, if a particular key has additional constraints, you will still need to
do that additional checking. For example, if you have a parameter that should be a positive int, you can depend on
`check_config` to make sure that the value is an int, but you will need to check that the value is positive.

Aside from these basic types, however, you should generally expect to do any conversion yourself - for example, 
timestamps from strings is something you will need to implement, ideally within your `__init__` method in
order to make repeated calls to your `validate` with the return of a previous call *idempotent*.

```
"""
Args:
    conf_dict (dict): The dictionary to be validated.

Raises:
    KeyError: If a required configuration option is missing. The exception message is
        the missing key and only the missing key.
    ValueError: If a configuration option's value is not valid. The error message
        should be in the following format:
        key: value reason

Returns:
    dict: The validated input dictionary with any missing optional parameters added with sane default values.
"""
```

# <a name="api">UserSim API Reference

## add\_feedback

```
"""
Create an additional feedback message. This will mostly be used from within threads supporting a main task, for example, managing interaction with an external program. 

Args:
    task_id (int): The task ID of the calling task. This can be accessed from within a task object by using self._task_id. If task_id < 1, no feedback will be generated.
    error (str): A description of the error, or a traceback.format_exc().
"""
```

## check\_config

```
""" Asserts that all of the types in config match the types in the description strings in parameters. In addition missing optional keys are added to the config from defaults.

Args:
    config (dict): A dictionary to check. Should contain all keys from parameters['required']. Each key's value must be of the same type specified in that key's description string in parameters (both required and optional).
    parameters (dict): The return from a task.parameters call. Contains two keys, 'required' and 'optional', whose values are dict objects containing the keys that are required to be in config, and optional ones that may be in config. In these sub-dicts, the values are description strings that have at least one ':' (colon) character. Everything before the last ':' character is loaded as YAML (preferably compact), and it should describe the expected type structure of that particular parameter. For example, a list of strings should be written as follows:
            '[str]: blah blah your description here'
        A dictionary whose keys are ints and values are strs should be as follows:
            '{int: str}: some description here'
        Valid type strings (the 'str' or 'int' above) are the following:
            str, int, float, bool, any, task
        Where 'any' includes any of the first four, while 'task' indicates that the parameter is actually a task dict which should be validated with validate_config.
    defaults (dict): A dictionary whose keys are the same as the keys in parameters['optional'], and whose values are sane defaults for those parameters. These values should still have the same type as indicated by the description string in parameters.

Raises:
    TypeError:

Returns:
    dict: config with its parameters type-checked, and missing optional values inserted.
"""
```

## external\_lookup

```
"""
Look up a variable external to the usersim. First looks at environment variables, then looks at VMWare guestinfo variables. Only returns a value for an exact match. 

Args:
    var_name (str): The name of the variable to lookup. 

Returns:
    str: Returns the value of the variable. If the variable is not found, returns an empty string.
"""
```

## get\_tasks

```
"""
Get the tasks and their (human-readable) parameters currently available to this simulation. Certain special tasks will be filtered by default. 

Args:
    filter_result (bool): True - filters special tasks, False - no filter is applied. 

Returns:
    dict of dicts of dicts: A dictionary whose keys are task names, and whose values are dictionaries whose keys are 'required' and 'optional', and whose values are dictionaries whose keys are the parameter name, and whose values are human-readable strings indicating what is expected for the parameter.
"""
```

## new\_task

```
"""
Inserts a new task into the user simulator. 

Args:
    task_config (dict): A dictionary with the following key:value pairs.
        'type':str
        'config':dict
    start_paused (bool): True if the new task should be paused initially, False otherwise.
    reset (bool): True if the simulator should be reset, False otherwise. This option should only be used for writing tests. 

Raises:
    KeyError: See validate_config docstring.
    ValueError: See validate_config docstring. 

Returns:
    int: The new task's unique ID.
"""
```

## pause\_all

```
"""
Pause all currently scheduled tasks.
"""
```

## pause\_task

```
"""
Pause a single task. 

Args:
    task_id (int > 0): The task ID returned by an earlier call to new_task. 

Returns:
    bool: True if the operation succeeded, False otherwise.
"""
```

## status\_all

```
"""
Get a list of the status of all managed tasks. 

Returns:
    list of dicts: Each dictionary will have the following key:value pairs:
        'id':int
        'type':str
        'state':str
        'status':str
"""
```

## status\_task

```
"""
Get the status of a single task. 

Args:
    task_id (int > 0): The task ID returned by an earlier call to new_task. 

Returns:
    dict: A dictionary with the following key:value pairs:
        'id':int
        'type':str
        'state':str
        'status':str
"""
```

## stop\_all

```
"""
Stop all tasks that are currently scheduled or paused.
"""
```

## stop\_task

```
"""
Stop a single task. 

Args:
    task_id (int > 0): The task ID returned by an earlier call to new_task. 

Returns:
    bool: True if the operation succeeded, False otherwise.
"""
```

## unpause\_all

```
"""
Unpause all currently paused tasks.
"""
```

## unpause\_task

```
"""
Unpause a single task. 

Args:
    task_id (int > 0): The task ID returned by an earlier call to new_task. 

Returns:
    bool: True if the operation succeeded, False otherwise.
"""
```

## validate\_config

```
"""
Validate a config dictionary without instantiating a Task subclass. 

Args:
    config (dict): A dictionary with the following key:value pairs.
        'type':str
        'config':dict 

Raises:
    KeyError: If a required key is missing from config or config['config'] or if the task type does not exist.
    ValueError: If the given value of an option under config['config'] is invalid. 

Returns:
    dict: The dictionary associated with config's 'config' key, after processing it with the given task's validate method. This does NOT include the 'type' and 'config' keys as above - only the actual configuration for the given task.
"""
```

# Creating a New Task

In this chapter, we'll be discussing how to create your own Task subclass. There will be a tutorial, followed by some
how-to information on some additional subjects not covered by the tutorial.

## Tutorial

In this tutorial, we'll create a task that, by default, will print out 'Hello, World!', but takes an optional parameter
that will change allow the user to specify a particular name to greet.

We'll begin by importing our task parent class and creating the declaration for our subclass:

\lstinputlisting{developer-content/imports}

It's important to note here that your module file **must** be the same as the name of your class, but lowercase.
Therefore, this file should be named `hellotask.py` and it should be in the `tasks` directory.

You should also give a short summary of what your task does as a class-level docstring, also shown in the example.

We'll define our very simple `__init__` method next:

\lstinputlisting{developer-content/init}

Since new task construction is guaranteed to call our `validate` method, we don't need to call it ourselves.
It doesn't hurt anything to call it, but it's a waste of a step.

We're going to write our `parameters` and `validate` methods next. First, `parameters`:

\lstinputlisting{developer-content/parameters}

Next, we'll write the `validate` method. Note that the `check_config` call takes care of a lot of
checking we'd otherwise need to do manually:

\lstinputlisting{developer-content/validate}

Next, we'll implement the `__call__` method:

\lstinputlisting{developer-content/call}

Finally, we'll implement the `cleanup`, `stop`, and lstinline{status} methods.

\lstinputlisting{developer-content/cleanupstopstatus}

Here is our complete task in one block of code:

\lstinputlisting{developer-content/imports}
\lstinputlisting{developer-content/init}
\lstinputlisting{developer-content/parameters}
\lstinputlisting{developer-content/validate}
\lstinputlisting{developer-content/call}
\lstinputlisting{developer-content/cleanupstopstatus}

## How-To Information

### Exceptions

Inevitably, your code will trigger an exception. If it's an exception that you want to handle in a particular way 
without failing, then by all means you should do that. However, you should **not** catch all exceptions everywhere 
in your code. The UserSim automatically catches the very general `Exception` type in every case where it uses
any method from a task. This means that you should only catch specific exceptions that you want to handle, and let every
other exception raise in order to let the UserSim catch it and generate a feedback message.

However, do note that there is one case where you will probably want to catch all exceptions, and that is in the
[Threads](#threads) subsection. If your task independently spawns and interacts with a 
thread, that thread's exceptions cannot  be caught by the UserSim. In that case, you will want to use the API function 
`add_feedback` in order to ensure that those exceptions still find their way into the feedback queue.

### <a name="shared"/>Sharing Objects Between Task Runs

As an example, say you want to interact with an external application on the machine. Generally, if you close the
reference to that application, you either close the application or, worse, the next time you open a new reference, you
will open a new instance of that application. The way to handle this is by creating a singleton-like class:

```
class SharedApplication(object):
    app_handle = None

    def __new__(cls):
        if not cls.app_handle:
            # Start the application and store its reference as a class-level variable.
            cls.app_handle = somelibrary.start_application()

        return cls
```

Now, from your `Task` subclass, you can do the following:

```
    def __init__(self, config):
        self._config = config
        self._application = SharedApplication().app_handle
```

While this may seem like a strange approach, when you could create a long-running task that keeps its application
reference for its lifetime, you would have to be content with either never changing the configuration (imagine an
Outlook send task where it only ever sent the same email to the same email address), or you would have to implement a
form of inter-task communication, and at that point this is going to be less strange.

### <a name="threads"/>Threads

Sometimes, your task must do things that can block for a while. Since the UserSim does not automatically thread tasks,
and each cycle is synchronous, you are responsible for recognizing that your task may take a while to finish. In such a
case, it's perfectly acceptable to spawn a thread from your task. However, remember that your task could potentially be 
used many times very quickly, if nested within a `frequency` or other meta-task.

Depending upon what kind of task you're writing, it may make sense to spawn such a thread and then make it a shared
thread, as mentioned in the [Sharing Objects Between Task Runs](#shared) subsection. This approach is used in the 
browser tasks already, and works quite well. You  will want to look at the `add_feedback` API call if you 
implement this approach, so that you can receive errors that occur within your thread.

### Using the API

You will likely want to take advantage of the UserSim API for some tasks. For example, you may want your task to accept
a configuration dictionary for another task, and then trigger that task after some condition has been met. In this case,
your task's `validate` method should probably validate that nested task's configuration with the 
`validate_config` API function. When it comes time to trigger that task, you will call `new_task` to
add it to the UserSim's internal structures, which will make the task trigger during the next cycle (unless you choose
to start it paused).

Note: pending the proposed change to the task `parameters` method, your validate may not need to call
`validate_config` at all.

Please see the [API Reference](#api) for the full API reference.

### Platform-Locked Tasks

It is expected that tasks that are specific to a particular platform are not importable on a platform which cannot run
that task. Naturally, if your task must do something differently depending on the platform, you can do that thing within
your task, and your task would still be considered cross-platform as long as the platform difference does not prevent
your task from running on different platforms.

### Tests

There is a `tests` directory in the source tree, in which a number of test modules exist. The only defined
structure is that there exists a `run_test` function in a test file. This test may cover nearly anything, but
generally should be limited to things that are testable programmatically without network dependencies, such as 
configuration. If you want to implement a test for your task, take a look at some of the existing tests for other tasks.

**Note that if your task only runs on a specific platform, say Windows, your test must check if it is running on the
right platform, and return if not.** This is typically done with a call to `platform.system()`, but this is up to you.

Example:
```
if not platform.system() == 'Windows':
    return
```

# Building the UserSim

This chapter discusses how to create a UserSim build, and steps you may need to take if your code works from source, but
the build does not seem to work.

## Building

Actually, creating a build will be extremely easy in most cases. All you need to do is run
`pyinstaller3 main.spec` (Linux) and PyInstaller will bundle your build under the `dist/` directory 
with a timestamp. On Windows, the `pyinstaller3` command may not be in the environment PATH variable, and you 
will need to locate the `pyinstaller.exe` executable under your Python installation's `Scripts/` 
folder. 

In both cases, it is very important that the PyInstaller command you are using is pointing to the one in the particular
Python version with which you are running the UserSim. For example, running `pyinstaller main.spec` on a Linux
distribution which has both Python 2.7 and Python 3.5 installed may actually point to the `pyinstaller` script
in the 2.7 installation, which will attempt to build UserSim with Python 2.7. This **will not** work, hence you
should specifically use `pyinstaller3` whenever it's available.

## Hooks

Usually, the PyInstaller build will work fine with no need to make modifications.

However, sometimes you will have tested your code, and it works from source, yet the built version inexplicably does not
work. This means you will need to create a PyInstaller hook. Most of the time, Python packages are pure code. Sometimes,
however, they rely upon data files. Often, these are supplementary text files or some binary data. Other times, they may
rely upon shared libraries (DLLs on Windows) which may not be present on the target system.

In such cases, you will need to investigate which files are missing. In the case of missing DLLs, often you will only 
need to install a Visual C++ redistributable on the target machine, and not actually need to create a hook file.

Unfortunately, with the sheer volume of Python libraries there is no one-size-fits-all hook for every package. The best
source for more information about hooks is to read the official PyInstaller documentation for hooks and examine the
hooks that are already in the `hooks/` directory.

Once you've created a hook for a task, you will then need to place it in the `hooks/` directory, and it must
be named `hook-tasks.yourtask.py` where `yourtask` exactly matches the name of your task.

