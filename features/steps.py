#!/usr/bin/python3
from aloe import *
import os
import subprocess
import uuid
import json
from . import interface

DIR_TMP = '/tmp'

def execute_command_line(args, cwd=None):
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         cwd=cwd,
                         shell=False)
    output = [ line.decode('utf-8') for line in p.stdout.readlines()]
    error = [ line.decode('utf-8') for line in p.stderr.readlines()]
    return output, error


@after.all
def remove_tmp_directory():
    execute_command_line(['rm', '-rf', world.repo_tmp])

@before.all
def set_tmp_directory():
    world.repo_tmp = DIR_TMP + '/'  + str(uuid.uuid4())


@step('I have a local repository in the current directory')
def have_local_repository(step):
    output, error = execute_command_line(['git', 'status'])
    assert len(output) > 0


@step('I check the git logs')
def check_git_logs(step):
    world.output, world.error = execute_command_line(
        ['git', 'log', '--pretty', '--format=oneline'])


@step('I view some commits')
def view_commits(step):
    assert len(world.output) > 0


@step('I check if there is a remote repository')
def check_remote_repository(step):
    world.output, world.error = execute_command_line(['git', 'remote', '-v'])


@step('I view the url of the remote repository')
def check_remote_url(step):
    assert len(world.output) >= 2
    assert world.output[0].find("(fetch)") > 0
    assert world.output[1].find("(push)") > 0
    world.remote_url = world.output[0][world.output[0].find(
        "\t") + 1:world.output[0].find(" (fetch)")]
    assert len(world.remote_url) > 0


@step('I have a remote repository linked to the local repository')
def have_remote_repository(step):
    step.given('I check if there is a remote repository')
    step.given('I view the url of the remote repository')


@step('I clone the remote repository in a temporary path')
def clone_remote_repository(step):
    execute_command_line(
        ['git', 'clone', world.remote_url, world.repo_tmp])
    output, error = execute_command_line(['ls', world.repo_tmp])
    assert len(error) == 0


@step('I view the same commits than in the local version')
def compare_commits(step):
    output_local, error_local = execute_command_line(
        ['git', 'log', '--pretty', '--format=oneline'])
    output_remote, error_remote = execute_command_line(
        ['git', 'log', '--pretty', '--format=oneline'],
        cwd=world.repo_tmp + '/')
    assert len(output_local) == len(output_remote)
    for line_local, line_remote in zip(output_local, output_remote):
        assert line_local[:line_local.find(
            ' ')] == line_remote[:line_remote.find(' ')]


@step('I have cloned the repository in a temporary path')
def have_cloned_repository(step):
    output, error = execute_command_line(['ls', world.repo_tmp])
    if len(error) > 0:
        step.given('I check if there is a remote repository')
        step.given('I view the url of the remote repository')
        step.given('I clone the remote repository in a temporary path')


@step('I list the tags')
def list_tags(step):
    world.output, world.error = execute_command_line(
        ['git', 'tag'], cwd=world.repo_tmp)


@step('I find "([^"]*)" in the list of tags')
def check_list_of_tags(step, tagname):
    assert tagname + '\n' in world.output


@step('I checkout the tag "([^"]*)"')
def checkout_tag(step, tagname):
    output, error = execute_command_line(
        ['git', 'checkout', tagname], cwd=world.repo_tmp)
    if len(error) > 0:
        assert error[-1].find('HEAD') > -1
    assert True


@step('I have checkout the tag "([^"]*)"')
def have_checkout_tag(step, tagname):
    step.given('I clone the remote repository in a temporary path')
    step.given('I checkout the tag "' + tagname + '"')


@step('I find a file named "([^"]*)"')
def find_file(step, filename):
    output, error = execute_command_line(['ls', filename], cwd=world.repo_tmp)
    assert len(error) == 0


@step('I have found a file named "([^"]*)" in the tag "([^"]*)"')
def have_found_file(step, filename, tagname):
    step.given('I have a remote repository linked to the local repository')
    step.given('I have checkout the tag "' + tagname + '"')
    step.given('I find a file named "' + filename + '"')


@step(' I check the contents of "([^"]*)"')
def check_contents_file(step, filename):
    world.output, world.error = execute_command_line(
        ['cat', filename], cwd=world.repo_tmp)
    assert len(world.error) == 0


@step('I view that each line contains a string, a comma and a string')
def check_file_format(step):
    assert len(world.output) > 0
    for line in world.output:
        pos_comma = line.find(',')
        if pos_comma <= 0 or pos_comma == len(line) - 1:
            assert False, 'Line "' + \
                line[:-1] + '" does not follow the format "surname, name"'
    assert True


@step('I list the files under version control')
def list_version_control_files(step):
    world.output, world.error = execute_command_line(['git', 'ls-files'])
    assert len(world.error) == 0

@step('I list the files under version control')
def list_version_control_files(step):
    world.output, world.error = execute_command_line(['git', 'ls-files'])
    assert len(world.error) == 0

@step('I view that "([^"]*)" is under version control')
def check_files_under_version_control(step, filename):
    found = False
    for line in world.output:
        if line[:-1] == filename:
            found = True
            break
    assert found

@step('I have found a file named "([^"]*)" in the local repository')
def is_file_in_local_repository(step, filename):
    step.given('I have a local repository in the current directory')
    step.given('I list the files under version control')
    step.given('I view that "' + filename + '" is under version control')


@step('I run "([^"]*)"')
def run_app(step, filename):
    interface.start('./' + filename)
    w = interface.onWidget('FRAME')
    world.output = w.get_name()
    interface.stop()

@step('I view that the app has a Gtk Window with the title "([^"]*)"')
def check_app(step, label):
    assert world.output == label


@step('I run "([^"]*)" in the temporary path')
def run_app_temporary_path(step, filename):
    interface.start(world.repo_tmp + '/' + filename)
    w = interface.onWidget('FRAME')
    world.output = w.get_name()
    interface.stop()
