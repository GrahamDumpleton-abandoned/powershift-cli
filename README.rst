This package provides a pluggable command line client called
``powershift``, for working with OpenShift. It acts as a wrapper around
the ``oc`` command line client for OpenShift, providing an easier to use
interface for using selected features of the ``oc`` client.

In particular, ``powershift`` provides a plugin which wraps the ``oc
cluster up`` command, used for starting up a local OpenShift cluster using
your local Docker service. This plugin builds on top of ``oc cluster up``,
to provide profiles, additional security, application persistence and
provisioning for persistent volumes.

System Requirements
-------------------

This package can be used on MacOS X, Windows and Linux.

The package requires the Python language interpreter to be available on
your system. You need to have available Python 2.7, 3.3, 3.4, 3.5 or 3.6,
and will need to have the Python package installer ``pip`` installed. It is
also recommended that you have ``virtualenv`` available and use ``pipsi``
to install the package into an isolated Python virtual environment. The use
of ``pipsi`` ensures that installing the package does not affect your
system Python installation.

As the ``powershift`` client is a wrapper around ``oc``, you need to have
the ``oc`` program for the version of OpenShift you wish to use installed
and available in your ``PATH``. If you do not already have ``oc``
installed, the ``powershift`` client can help you with it's installation.

Versions of ``oc`` for OpenShift Origin, which ``powershift`` has been
tested with are 1.3.2, 1.3.3 and 1.4.0. If using Red Hat OpenShift
Container Platform, you need to have a minimum of version 3.4.0 of the
``oc`` tool and your system must have access to the Red Hat registry
associated with your Red Hat subscription.

Docker installation types which can be used are Docker for Mac, Docker for
Windows or Docker running natively on Linux. You cannot use a Docker
instance configured using ``docker-machine``, or the older means of running
Docker on MacOSX based on ``boot2docker``.

Installing 'powershift'
-----------------------

It is recommend that you use ``pipsi`` to install ``powershift``. This
ensures that it and any Python packages it requires are installed into a
self contained Python virtual environment and will not interfere with any
other Python based applications installed on your system.

For the most up to date instructions on how to first install ``pipsi``
see:

* https://pypi.python.org/pypi/pipsi

The recommended way to install ``pipsi`` is to run::

    curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python

This command will install ``pipsi`` and then output the directory which you
should add to your ``PATH`` so that it and any script packages installed
using ``pipsi`` can be found.

Once ``pipsi`` is installed and in your ``PATH``, to install this package,
along with currently available plugins, run::

    pipsi install powershift-cli[all]

Additional plugins which are installed will be:

* `powershift-cluster`_ - Adds command providing a layer around the ``oc
  cluster up`` command for running a local OpenShift instance with Docker.
  These make it easier to manage a local OpenShift cluster, including
  default support for application persistence across restarts, multiple
  profiles, added security, default persistent volumes, and tools for
  adding additional persistent volumes to the local OpenShift cluster.

.. _`powershift-cluster`: https://github.com/getwarped/powershift-cluster

If you are happy to install this package directly into your main Python
installation or have an existing Python virtual environment, you can
instead run::

    pip install powershift-cli[all]

If necessary, run this as root using ``sudo``, when installing into your
system Python installation.

Additional Python packages installed by this package and current plugins
are ``click`` and ``passlib``.

Installing 'oc' client
----------------------

If you have the ``oc`` program installed already, ensure it is installed
somewhere on your default ``PATH``.

If you do not yet have the ``oc`` program installed, you can install it
using the ``powershift`` program.

As the first step run::

    powershift client versions

This will list what versions of the ``oc`` program for OpenShift Origin
the script knows about. You can then install one of these versions.
For example::

    powershift client install v1.4.0

The platform you are using will be automatically detected and the
appropriate binary downloaded and installed. For Linux, only 64 bit
platforms are supported using this command.

The output of this command will provide the directory you should then add
to your ``PATH``.

If you would rather have it install the ``oc`` program into an existing
directory already in your ``PATH``, you can instead use the ``--bindir``
option to specify the directory to install into. For example::

    powershift client install v1.4.0 --bindir $HOME/bin

Command line help
-----------------

Executing the command with no arguments will provide a list of the
command groups available.

::

    $ powershift
    Usage: powershift [OPTIONS] COMMAND [ARGS]...

      PowerShift client for OpenShift.

      This client provides additional functionality useful to users of the
      OpenShift platform. Base functionality is minimal, but can be extended by
      installing additional plugins.

      For more details see:

          https://github.com/getwarped/powershift

    Options:
      --help  Show this message and exit.

    Commands:
      client      Install/update oc command line tool.
      completion  Output completion script for specified shell.
      console     Open a browser on the OpenShift web console.
      server      Displays the URL for the OpenShift cluster.
      session     Display information about current session.

This only shows command groups included with the base package. When you
install additional plugins, the command groups they add will also be shown.

You can use the ``--help`` option with any command group or specific
command to get additional details.

Bash shell completion
---------------------

To enable ``bash`` completion, run ``powershift completion bash --help``
and follow the instructions.
