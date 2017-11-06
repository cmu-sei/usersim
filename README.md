The User Simulator is a tool designed to generate network and host activity for training purposes. It is intended for
use in a closed network primarily consisting of Windows and Linux virtual machines. Other operating systems may be
compatible, but are untested. The Linux version does not have access to all the features of the Windows version. In
particular, the Windows version can run several of the programs in MS Office, while the Linux version obviously cannot.

This project is distributed under a BSD [license](LICENSE.md). Carnegie Mellon University retains the 
[copyright](COPYRIGHT.md).

See the [Developer's Guide](docs/developer-guide.md) for source installation and build instructions.
Once all required Python libraries have been installed, you should run `python gendocs.py` in your virtual
environment in order to create the [Task Reference](docs/tasks.md) and [API Reference](docs/api-reference.md) files.
These files will be generated and included automatically upon creating a build.

See the [User Guide](docs/user-guide.md) for end-user instructions.
