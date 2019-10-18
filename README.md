# System Service Library for Python

This is a library to assist with controlling system services.

## Classes

### ServiceConfig

The `ServiceConfig` class is created to simplify/unify creation of configuration files, as these come in all types of shapes ans sizes.  This currently only supports `jsonarray`, `ini`, `blocks`, and `raw`.  This was originally designed because I was tired of writing a new library every time I wanted an interface for configuration files.

#### Parameters

- `filepath`  - (*required*) The full path to the file on the system.
- `filetype`  - (*required*) The type of configuration file, currently only supports `jsonarray`, `ini`, `blocks`, and `raw`.
- `blocks`    - An array of pre-defined Block objects; may be used for loading a saved state (default: `None`)
- `closer`    - The character to end each setting (default: <empty string>)
- `definer`   - The character that is used to separate the key from the value in the configuration file (default: `=`)
- `commenter` - The character that is used for creating comments

#### How to Use `ServiceConfig`

Let's take, for example, the `/etc/libuser.conf` file.

First, we create a `ServiceConfig` instance.

```
import serviceconf

LIBUSERCONF=serviceconf.ServiceConfig('/etc/libuser.conf','ini')
```

Next, we create a new block and add the related settings.  Each setting that is added directly after the addition of a block is attached to that specific block.

```
LIBUSERCONF.add_block('import')
LIBUSERCONF.add_setting('login_defs','/etc/login.defs')
LIBUSERCONF.add_setting('default_useradd','/etc/default/useradd')
```

We can create additional blocks with additional settings.

```
LIBUSERCONF.add_block('defaults')
LIBUSERCONF.add_setting('moduledir','/etc/libuser.conf.d/modules')
LIBUSERCONF.add_setting('crypt_style','sha512')
LIBUSERCONF.save()
```

This produces the following:

```
[import]
login_defs=/etc/login.defs
default_useradd=/etc/default/useradd

[defaults]
moduledir=/etc/libuser.conf.d/modules
crypt_style=sha512


```

### Service Config File Types

#### `ini` files

Typically, **ini** files have blocks that are bracketed, then groups of settings following the bracketed word.  Often the settings are in the format of `key = value`, sometimes ending with a semi-colon: `key = value;`.

##### Example `ini` file

```
[ldap]
server = ldap.digitalocean.com
basedn = dc=example,dc=com
```

#### `jsonarray`

For `ServiceConfig`, **jsonarray** is actually an array of `jsonarray` settings.  This allows for multiple configurations of the same type.  While this output isn't typical, it allows for multiple settings.  For example a system that allows for multiple server definitions would look like this:

```
[
  {
    "server": {
      "bind_address": "0.0.0.0",
      "port": "1234"
    }
  },
  {
    "server": {
      "bind_address": "0.0.0.0",
      "port": "5678"
    }
  }
]
```

##### Example `jsonarray` file

```
[
  {
    "import": {
      "login_defs": "/etc/login.defs",
      "default_useradd": "/etc/default/useradd"
    }
  },
  {
    "defaults": {
      "moduledir": "/etc/libuser.conf.d/modules",
      "crypt_style": "sha512"
    }
  }
]
```

#### `blocks`

A **blocks** definition place settings within bracketed (or braced) blocks.  This isn't typical for many configuration files, but has been seen in configurations, such as *Redsocks*.

##### Example `blocks` file

In this example, it's also worth noting that the `closer` was used and set to a semi-colon.

```
server {
bind_address=0.0.0.0;
port=1234;
}
server {
bind_address=0.0.0.0;
port=5678;
}
```

### ServiceApi

The `ServiceApi` class is created to simplify/unify control of system services via Rest-like API.

#### Requirements

This module requires the `PolicyKit-1` package for controlling the systemd bus.

#### Parameters

- `servicename`  - (*required*) The name of the service (sans `.service`).  For example, if this was `nginx.service`, you would use `servicename=nginx`.

#### Functions

- `get_sysd_manager_interface` - Used for controlling the systemd bus.

#### Methods

##### `dbus_action(action)`

This applies the `action` to the service.  **Action** must be one of `start`, `stop`, and `restart`.

##### `dbus_getstate()`

This gets the current state of the service.  It returns a dictionary that indicates the `active_state` and `sub_state`.  For example: `inactive (dead)` = `{'active_state': 'inactive', 'sub_state': 'dead'}`.

##### `enable()`

Creates the symbolic links to the service in `/etc/systemd/system/multi-user.target.wants` (from `/lib/systemd/system/<servicename>.service`).  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `disable()`

Removes the symbolic links to the service in `/etc/systemd/system/multi-user.target.wants` (from `/lib/systemd/system/<servicename>.service`).  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `start()`

Starts the service using the `dbus_action` method.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `stop()`

Stops the service using the `dbus_action` method.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `restart()`

Restarts the service using the `dbus_action` method.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `status()`

Gets the service status using the `dbus_getstate` method.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `servicectl()`

Controls the service using the `enable`, `disable`, `start`, `stop`, `status`, or `restart` methods.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `enable_and_start()`

Uses the `enable` and `start` methods to enable the service and start the service.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

##### `disable_and_stop()`

Uses the `disable` and `stop` methods to enable the service and start the service.  Returns a dictionary that includes a `message` (array of strings), and a `status` (integer return value (`0` = successful).

