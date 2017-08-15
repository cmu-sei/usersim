import platform
from subprocess import PIPE, Popen


if platform.system() == 'Windows':
    path = '"C:\\Program Files\\VMWare\\VMWare Tools\\vmtoolsd.exe"'
else:
    # It's likely to be in the path on non-Windows systems.
    path = 'vmtoolsd'

command = path + ' ' + '--cmd "info-get guestinfo.{}"'

def lookup(var_name):
    """ Attempts to use the system vmtoolsd to lookup the variable.
    SECURITY ALERT: It's trivial to inject malicious actions into var_name, but that's not currently an issue. This may
    need to be sanitized later.

    Returns:
        str:
    """
    process = Popen(command.format(var_name), stdout=PIPE, stderr=PIPE, shell=True)
    if process.stderr.read():
        return str()
    else:
        value = process.stdout.read().decode().strip()

    return value
