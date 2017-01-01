import os
import sys
import re
import subprocess
import webbrowser
import zipfile
import tarfile
import stat

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

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

@root.command()
def console():
    """
    Open a browser on the OpenShift web console.

    """

    webbrowser.open(server_url())

@root.command()
def server():
    """
    Displays the URL for the OpenShift cluster.

    """

    click.echo(server_url())

@root.group()
def completion():
    """
    Output completion script for specified shell.

    """

    pass

@completion.command()
def bash():
    """
    Output shell completion code for 'bash'.

    To generate the completion code and enable it use:

    \b
        powershift completion bash > powershift-complete.sh
        source powershift-complete.sh

    """

    directory = os.path.dirname(__file__)
    script = os.path.join(directory, 'completion-bash.sh')
    with open(script, encoding='UTF-8') as fp:
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

@root.group()
def session():
    """
    Display information about current session.

    """

@session.command()
@click.pass_context
def user(ctx):
    """
    Displays name of user for active session.

    """

    try:
        click.echo(session_user())
    except subprocess.CalledProcessError as e:
        click.echo('Failed: %s' % e.stdout)
        ctx.exit(e.returncode)

@session.command()
@click.pass_context
def context(ctx):
    """
    Displays the active user session context.

    """

    try:
        click.echo(session_context())
    except subprocess.CalledProcessError as e:
        click.echo('Failed: %s' % e.stdout)
        ctx.exit(e.returncode)

@session.command()
@click.pass_context
def token(ctx):
    """
    Displays the active user session token.

    """

    try:
        click.echo(session_token())
    except subprocess.CalledProcessError as e:
        click.echo('Failed: %s' % e.stdout)
        ctx.exit(e.returncode)

@root.group()
def client():
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
    'v1.4.0-rc1': {
        'darwin' : 'openshift-origin-client-tools-v1.4.0-rc1.b4e0954-mac.zip',
        'linux' : 'openshift-origin-client-tools-v1.4.0-rc1.b4e0954-linux-64bit.tar.gz',
        'win32' : 'openshift-origin-client-tools-v1.4.0-rc1.b4e0954-windows.zip',
    }
}

@client.command()
@click.pass_context
def versions(ctx):
    """
    List versions of oc that can be installed.

    """

    for version in client_downloads:
        click.echo(version)

@client.command()
@click.pass_context
@click.option('--bindir', default=None,
    help='Specify directory to install oc binary.')
@click.argument('version', default='v1.3.2')
def install(ctx, version, bindir):
    """
    Install version of oc command line tool.

    """

    if version not in client_downloads:
        click.echo('Failed: Version not available for installation.')
        ctx.exit(1)

    if sys.platform not in client_downloads[version]:
        click.echo('Failed: Version not available for platform.')
        ctx.exit(1)

    # Create a directory for holding install oc binary.

    if bindir is None:
        rootdir = ctx.obj['ROOTDIR']
        bindir = os.path.join(rootdir, 'tools')

    os.makedirs(bindir, exist_ok=True)

    # Download the package.

    filename = client_downloads[version][sys.platform]

    url = '%s/%s/%s' % (download_prefix, version, filename)

    click.echo('Downloading: %s' % url)

    local_filename, headers = urlretrieve(url)

    try:
        if filename.endswith('.zip'):
            with zipfile.ZipFile(local_filename, 'r') as zfp:
                binary = list(filter(lambda name: name in ['oc', 'oc.exe'],
                        zfp.namelist()))[0]
                click.echo('Extracting: %s' % binary)
                zfp.extract(binary, bindir)

        elif filename.endswith('.tar.gz'):
            with tarfile.open(local_filename, 'r:gz') as tfp:
                binary = list(filter(lambda name: name.endswith('/oc'),
                        tfp.getnames()))[0]
                click.echo('Extracting: %s' % binary)
                with tfp.extractfile(binary) as src:
                    with open(os.path.join(bindir, 'oc'), 'wb') as dst:
                        dst.write(src.read())
                binary = os.path.basename(binary)

    finally:
        try:
            os.unlink(local_filename)
        except OSError:
            pass

    # Make file executable.

    path = os.path.join(bindir, binary)

    info = os.stat(path)
    os.chmod(path, info.st_mode|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)

    click.echo('Success: Ensure that %r is in your "PATH".' % bindir)

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
