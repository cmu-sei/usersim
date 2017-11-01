# Introduction

This guide discusses how to use a UserSim binary. The first section lists any requirements for actually getting the
UserSim to be able to run. The second section goes into the command line arguments for starting the program. Finally,
the last section is a tutorial for constructing a configuration file in YAML.

# Requirements

## All Platforms

To use the `firefox` task, you must have installed a version of Firefox on your system, preferably a recent one.

## Windows

On older Windows versions, you may need to install the Microsoft Visual C++ 2015 redistributable in order for UserSim to
run.

To use the full functionality of the UserSim, you will need to install a 32-bit version of an Office Suite. Currently,
2007-2016 should work. You will also need to install Outlook Redemption from
<http://www.dimastr.com/redemption/home.htm> in order to let the UserSim interact with Outlook. You may need to purchase
a license, depending upon your needs (SEI already has one for internal use).

## Linux

Currently, there are no Linux-specific tasks.

# Starting the UserSim

When starting the UserSim, you must select which mode it will start in. There is currently no default mode.

## `local` Mode

This mode starts the UserSim with a path to a YAML configuration file. By default, `example.yaml` is loaded from the
working directory. Otherwise, supply a path to a UserSim configuration as the first argument.

Example:
`./usersim local /path/to/config.yaml`

## `xga` Mode

Starts the UserSim in XGA communication mode. SEI internal. Feedback exceptions will be written to a rotating log file
named `~/feedbackX.log` where X is between 1-5 (that's in the logged-in user's home directory).

Example:
`./usersim xga`

## `rpc` Mode - Not Yet Complete

**SUBJECT TO CHANGE**

This mode is currently **NOT SECURE**, and thus should only be used in closed networks.

Connects to a UserSim server node, allowing enhanced interaction with UserSim clients. Supports the following positional
arguments:

* ip_address: Server node's address. Defaults to `127.0.0.1`.
* port: Port on which the server is listening. Defaults to `18812`.
* name: An arbitrary identifier to be given to the server node.

Example:
`./usersim rpc 192.168.0.150 12345 hello`

# Tutorial: Creating a YAML Configuration

For this tutorial, we're going to create a configuration which uses the `attime` task to schedule a `frequency` task to 
run at 9 AM (tomorrow, if it's later than 9 AM today). This task will then periodically trigger a `firefox` task to
browse to one of a few possible websites.

First, let's start with the `attime` task:

```
- type: attime
  config:
    task:
    time: "0900"
```

Now, we need to nest the `frequency` task under the `attime` task. Let's set it to trigger about 5 times per hour, and
let it trigger a total of 20 times:

```
- type: attime
  config:
    task:
      type: frequency
      config:
        frequency: 5
        repetitions: 20
        task:
    time: "0900"
```

Finally, we'll add the `firefox` task. We'll let it choose between <https://www.google.com>, <http://www.cnn.com>, and
<https://www.sei.cmu.edu>. As specified in the `firefox` task documentation, the sites specified for the `firefox` task
must be fully-qualified domain names (FQDN).

```
- type: attime
  config:
    task:
      type: frequency
      config:
        frequency: 5
        repetitions: 20
        task:
          type: firefox
          config:
            sites:
              - https://www.google.com
              - http://www.cnn.com
              - https://www.sei.cmu.edu
    time: "0900"
```
