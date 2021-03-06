# -*- coding: utf-8 -*-

import os
import shutil
import sys
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

from invoke import task
# from invoke.util import cd
from pelican.server import ComplexHTTPRequestHandler

CONFIG = {
    # Local path configuration (can be absolute or relative to tasks.py)
    'deploy_path': 'output-publish',
    # Remote server configuration
    'production': 'rankurusu.veekun.com',
    'dest_path': '/var/www/eev.ee',
    # Rackspace Cloud Files configuration settings
    # 'cloudfiles_username': '{{cloudfiles_username}}',
    # 'cloudfiles_api_key': '{{cloudfiles_api_key}}',
    # 'cloudfiles_container': '{{cloudfiles_container}}',
    # Github Pages configuration
    # 'github_pages_branch': '{{github_pages_branch}}',
    # Port for `serve`
    'port': 8001,
}


@task
def clean(c):
    """Remove generated files"""
    if os.path.isdir(CONFIG['deploy_path']):
        shutil.rmtree(CONFIG['deploy_path'])
        os.makedirs(CONFIG['deploy_path'])


@task
def build(c):
    """Build local version of site"""
    c.run('pelican -s pelicanconf.py')


@task
def rebuild(c):
    """`build` with the delete switch"""
    c.run('pelican -d -s pelicanconf.py')


@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    c.run('pelican -r -s pelicanconf.py')


@task
def serve(c):
    """Serve site at http://localhost:8000/"""
    os.chdir(CONFIG['deploy_path'])

    class AddressReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        ('', CONFIG['port']),
        ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {port} ...\n'.format(**CONFIG))
    server.serve_forever()


@task
def reserve(c):
    """`build`, then `serve`"""
    build(c)
    serve(c)


@task
def preview(c):
    """Build production version of site"""
    c.run('pelican -s publishconf.py')


# @task
# def cf_upload(c):
#     """Publish to Rackspace Cloud Files"""
#     rebuild(c)
#     with cd(CONFIG['deploy_path']):
#         c.run('swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
#               '-U {cloudfiles_username} '
#               '-K {cloudfiles_api_key} '
#               'upload -c {cloudfiles_container} .'.format(**CONFIG))


@task
def publish(c):
    """Publish to production via rsync"""
    c.run('pelican -s publishconf.py')
    c.run(
        'rsync --delete --exclude ".DS_Store" -pthrvz -c '
        '{} {production}:{dest_path}'.format(
            CONFIG['deploy_path'].rstrip('/') + '/',
            **CONFIG))


# @task
# def gh_pages(c):
#     """Publish to GitHub Pages"""
#     rebuild(c)
#     c.run("ghp-import -b {github_pages_branch} {deploy_path} -p".format(
#         **CONFIG))
