import os
import sys
import re
import subprocess
import webbrowser
import zipfile
import tarfile
import stat
import shutil

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

import click

if sys.platform == 'win32':
    SAVEDIR='PowerShift'
else:
    SAVEDIR='.powershift'

DEFAULT_ROOTDIR = os.path.expanduser(os.path.join('~', SAVEDIR))
ROOTDIR = os.environ.get('POWERSHIFT_HOME_DIR', DEFAULT_ROOTDIR)

ENTRYPOINTS = 'powershift_cli_plugins'

def server_url():
    # XXX This is only available from Origin 1.4 onwards.
    # command = ['oc', 'whoami', '--show-server']
    # url = subprocess.check_output(command, universal_newlines=True)
    # url = url.strip()

    command = ['oc', 'config', 'view', '--minify', '-o',
            'jsonpath="{.clusters[*].cluster.server}"']

    url = subprocess.check_output(command, universal_newlines=True)
    url = re.sub(r'^\s*"(.*)"\s*$', r'\1', url)

    return url

@click.group()
@click.pass_context
def root(ctx):
    """
    PowerShift client for OpenShift.

    This client provides additional functionality useful to users of the
    OpenShift platform. Base functionality is minimal, but can be extended
    by installing additional plugins.

    For more details see:

        https://github.com/getwarped/powershift

    """

    ctx.obj['ROOTDIR'] = ROOTDIR

    # If running a command from client group, we want to skip checks for
    # whether we have the 'oc' command as may be wanting to install it.

    if ctx.invoked_subcommand == 'client':
        return

    # Check whether the 'oc' command is installed and fail if not. We
    # are so dependent on it being installed that there isn't much point
    # continuing if it isn't.

    try:
        subprocess.check_output(['oc', 'help'], stderr=subprocess.STDOUT)

    except FileNotFoundError:
        click.echo('Failed: You do not appear to have the \'oc\' command '
                'line tool installed. Please install it to continue.')
        ctx.exit(1)

    except subprocess.CalledProcessError:
        click.echo('Failed: You appear to have the \'oc\' command '
                'line tool installed, but it appears to be non functional.')
        ctx.exit(1)

@root.command('console')
def command_console():
    """
    Open a browser on the OpenShift web console.

    """

    webbrowser.open(server_url())

@root.command('server')
def command_server():
    """
    Displays the URL for the OpenShift cluster.

    """

    click.echo(server_url())

@root.group('completion')
def group_completion():
    """
    Output completion script for specified shell.

    """

    pass

@group_completion.command('bash')
def command_completion_bash():
    """
    Output shell completion code for 'bash'.

    To generate the completion code and enable it use:

    \b
        powershift completion bash > powershift-complete.sh
        source powershift-complete.sh

    """

    directory = os.path.dirname(__file__)
    script = os.path.join(directory, 'completion-bash.sh')
    with open(script) as fp:
        click.echo(fp.read())

def session_context():
    command = ['oc', 'whoami', '-c']

    context = subprocess.check_output(command, stderr=subprocess.STDOUT,
            universal_newlines=True)
    context = context.strip()

    return context

def session_token():
    command = ['oc', 'whoami', '-t']

    token = subprocess.check_output(command, stderr=subprocess.STDOUT,
            universal_newlines=True)
    token = token.strip()

    return token

def session_user():
    command = ['oc', 'whoami']

    token = subprocess.check_output(command, stderr=subprocess.STDOUT,
            universal_newlines=True)
    token = token.strip()

    return token

@root.group('session')
def group_session():
    """
    Display information about current session.

    """

@group_session.command('user')
@click.pass_context
def command_session_user(ctx):
    """
    Displays name of user for active session.

    """

    try:
        click.echo(session_user())
    except subprocess.CalledProcessError as e:
        click.echo('Failed: %s' % e.stdout)
        ctx.exit(e.returncode)

@group_session.command('context')
@click.pass_context
def command_session_context(ctx):
    """
    Displays the active user session context.

    """

    try:
        click.echo(session_context())
    except subprocess.CalledProcessError as e:
        click.echo('Failed: %s' % e.stdout)
        ctx.exit(e.returncode)

@group_session.command('token')
@click.pass_context
def command_session_token(ctx):
    """
    Displays the active user session token.

    """

    try:
        click.echo(session_token())
    except subprocess.CalledProcessError as e:
        click.echo('Failed: %s' % e.stdout)
        ctx.exit(e.returncode)

@root.group('client')
def group_client():
    """
    Install/update oc command line tool.

    """

download_prefix = 'https://github.com/openshift/origin/releases/download'

client_downloads = {
    'v1.3.2': {
        'darwin' : 'openshift-origin-client-tools-v1.3.2-ac1d579-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.3.2-ac1d579-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.3.2-ac1d579-windows.zip',
    },
    'v1.3.3': {
        'darwin' : 'openshift-origin-client-tools-v1.3.3-bc17c1527938fa03b719e1a117d584442e3727b8-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.3.3-bc17c1527938fa03b719e1a117d584442e3727b8-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.3.3-bc17c1527938fa03b719e1a117d584442e3727b8-windows.zip',
    },
    'v1.4.0': {
        'darwin' : 'openshift-origin-client-tools-v1.4.0-208f053-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.4.0-208f053-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.4.0-208f053-windows.zip',
    },
    'v1.4.1': {
        'darwin' : 'openshift-origin-client-tools-v1.4.1-3f9807a-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.4.1-3f9807a-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.4.1-3f9807a-windows.zip',
    },
    'v1.5.0': {
        'darwin' : 'openshift-origin-client-tools-v1.5.0-031cbe4-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.5.0-031cbe4-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.5.0-031cbe4-windows.zip',
    },
    'v1.5.1': {
        'darwin' : 'openshift-origin-client-tools-v1.5.1-7b451fc-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.5.1-7b451fc-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.5.1-7b451fc-windows.zip',
    },
    'v3.6.0-alpha.1': {
        'darwin' : 'openshift-origin-client-tools-v3.6.0-alpha.1-46942ad-mac.zip',
        'linux' : 'openshift-origin-client-tools-v3.6.0-alpha.1-46942ad-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v3.6.0-alpha.1-46942ad-windows.zip',
    },
    'v3.6.0-alpha.2': {
        'darwin' : 'openshift-origin-client-tools-v3.6.0-alpha.2-3c221d5-mac.zip',
        'linux' : 'openshift-origin-client-tools-v3.6.0-alpha.2-3c221d5-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v3.6.0-alpha.2-3c221d5-windows.zip',
    }
}

@group_client.command('versions')
@click.pass_context
def command_client_versions(ctx):
    """
    List versions of oc that can be installed.

    """

    for version in sorted(client_downloads):
        click.echo(version)

@group_client.command('install')
@click.pass_context
@click.option('--bindir', default=None,
    help='Specify directory to install oc binary.')
@click.argument('version', default='v1.5.1')
def command_client_install(ctx, version, bindir):
    """
    Install version of oc command line tool.

    """

    if version not in client_downloads:
        click.echo('Failed: Version not available for installation.')
        ctx.exit(1)

    platform = sys.platform
    if platform.startswith('linux'):
        platform = 'linux'

    if platform not in client_downloads[version]:
        click.echo('Failed: Version not available for platform.')
        ctx.exit(1)

    # Create a directory for holding install oc binary.

    rootdir = ctx.obj['ROOTDIR']

    cachedir = os.path.join(rootdir, 'tools')

    if bindir is None:
        bindir = cachedir

    try:
        os.mkdir(rootdir)
    except OSError:
        pass

    try:
        os.mkdir(cachedir)
    except OSError:
        pass

    try:
        os.mkdir(bindir)
    except OSError:
        pass

    # Download the package.

    if sys.platform == 'win32':
        target = '%s/oc.exe' % version
        binary = 'oc.exe'
    else:
        target = '%s/oc' % version
        binary = 'oc'

    cache_path = os.path.join(cachedir, target)
    binary_path = os.path.join(bindir, binary)

    if not os.path.exists(cache_path):
        filename = client_downloads[version][platform]

        url = '%s/%s/%s' % (download_prefix, version, filename)

        click.echo('Downloading: %s' % url)

        local_filename, headers = urlretrieve(url)

        try:
            if filename.endswith('.zip'):
                with zipfile.ZipFile(local_filename, 'r') as zfp:
                    binary_file = binary

                    click.echo('Extracting: %s' % binary_file)

                    zfp.extract(binary_file, os.path.dirname(cache_path))

            elif filename.endswith('.tar.gz'):
                with tarfile.open(local_filename, 'r:gz') as tfp:
                    binary_file = list(filter(lambda name: name.endswith(
                            '/%s' % binary), tfp.getnames()))[0]

                    click.echo('Extracting: %s' % binary_file)

                    src = tfp.extractfile(binary_file)

                    try:
                        os.mkdir(os.path.dirname(cache_path))
                    except OSError:
                        pass

                    try:
                        with open(cache_path, 'wb') as dst:
                            dst.write(src.read())
                    finally:
                        src.close()

        finally:
            try:
                os.unlink(local_filename)
            except OSError:
                pass

        # Make file executable.

        info = os.stat(cache_path)
        mode = info.st_mode|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH
        os.chmod(cache_path, mode)

    else:
        click.echo('Using: %s' % cache_path)

    # Link versioned name to unversioned.

    try:
        os.unlink(binary_path)
    except OSError:
        pass

    shutil.copy(cache_path, binary_path)

    click.echo('Success: Ensure that "%s" is in your "PATH".' % bindir)

@group_client.command('env')
@click.pass_context
@click.option('--shell', default=None,
    help='Force environment to be for specific shell.')
@click.argument('version', default='unknown')
def command_client_env(ctx, version, shell):
    """
    Display the commands to set up the environment.

    """

    if version == 'unknown':
        version = None

    rootdir = ctx.obj['ROOTDIR']
    bindir = os.path.join(rootdir, 'tools')

    if version:
        bindir = os.path.join(bindir, version)

    if shell is None:
        if sys.platform == 'win32':
            shell = 'powershell'
        else:
            shell = 'sh'

    if shell in ('sh', 'bash'):
        click.echo('export PATH="%s:$PATH"' % bindir)
        click.echo('# Run this command to configure your shell:')
        if version:
            click.echo('# eval "$(powershift client env %s --shell=%s)"' %
                       (version, shell))
        else:
            click.echo('# eval "$(powershift client env --shell=%s)"' % shell)

    elif shell == 'powershell':
        click.echo('$Env:Path = "%s;" + $Env:Path' % bindir)
        click.echo('# Run this command to configure your shell:')
        if version:
            click.echo('# powershift client env %s --shell=powershell | Invoke-Expression' % version)
        else:
            click.echo('# powershift client env --shell=powershell | Invoke-Expression')

    elif shell == 'cmd':
        click.echo('set Path="%s;%%Path%%"' % bindir)
        click.echo('# Run this command to configure your shell: copy and paste the above values into your command prompt')

def main():
    # Import any plugins for extending the available commands. They
    # should automatically register themselves against the appropriate
    # CLI command group.

    try:
        import pkg_resources
    except ImportError:
        pass
    else:
        entrypoints = pkg_resources.iter_entry_points(group=ENTRYPOINTS)

        for entrypoint in entrypoints:
            __import__(entrypoint.module_name)

    # Call the CLI to process the command line arguments and execute
    # the appropriate action.

    root(obj={})

if __name__ == '__main__':
    main()
