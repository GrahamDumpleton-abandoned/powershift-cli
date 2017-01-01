This package provides a pluggable command line client for working with
OpenShift.

Note that you need to have already installed the OpenShift ``oc`` command
line client.

Command line help
-----------------

Executing the command with no arguments will provide a list of the base
commands available.

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
      completion  Output completion script for specified shell.
      console     Open a browser on the OpenShift web console.
      server      Displays the URL for the OpenShift cluster.

Bash shell completion
---------------------

To enable ``bash`` completion, run ``powershift completion bash --help``
and follow the instructions.

Available plugin modules
------------------------

The client uses a plugin structure so that additional commands can be added
for specific purposes by installing additional Python packages which define
the commands.

Additonal modules that are available which can be installed to extend the
available commands are:

* `powershift-cluster`_ - Adds command providing a layer around the ``oc
  cluster up`` command for running a local OpenShift instance with Docker.
  These make it easier to manage a local OpenShift cluster, including
  default support for persistence across restarts, multiple profiles and
  tools for adding persistent volumes to the local OpenShift cluster.

Use ``pip install`` to install any plugin modules. Once installed they will
be automatically enabled and commands made available.

.. _`powershift-cluster`: https://github.com/getwarped/powershift-cluster
