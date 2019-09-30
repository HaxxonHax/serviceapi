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

### Example `blocks` file

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

