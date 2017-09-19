#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Sólo python 3
#   Usa una construcción yield from que no hay en python 2

# >>> import interface
# >>> interface.start("lista_textos.py")
# >>> w = interface.onWidget("FRAME")
# >>> w.name
# >>> w = interface.onWidget("#File")
# >>> w >> interface.perform('click')
# >>> w >> interface.perform('click')
# >>> inteface.onWidget("#File") >> interface.perform('click')

import os
import subprocess
import random
import sys
import time

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

try:
    callable
except NameError:
    # python 3.0 - 3.1
    import collections
    callable = lambda o: isinstance(o, collections.Callable)

def _perform_action(self, name):
    iface = self.get_action_iface()
    for i in range(0, iface.get_n_actions()):
        if (iface.get_action_name(i) == name):
            iface.do_action(i)
            return
    raise Exception("Widget {} has no action named {}".format(self.get_name(), name))

def _func_pipe(self, f):
    if (not(callable(f))):
        raise TypeError("{} is not callable".format(f))
    return f(self)

Atspi.Accessible.perform = _perform_action
Atspi.Accessible.__rshift__ = _func_pipe

__MODULE__ = sys.modules[__name__]
__MODULE__.app_process = None
__MODULE__.app_obj = None

# app_path: path to the app begin tested
# stubbornness: number of times to try to find the app in the atspi registry after launching it
def start(app_path, stubbornness=2):
    if (__MODULE__.app_process is not None):
        if (__MODULE__.app_process.poll() is not None):
            raise RuntimeError("Didn't stopped already initialized app before initializing a new one.")
        else:
            stop()

    os.environ['GTK_MODULES'] = 'gail:atk-bridge'
    os.environ['LC_ALL'] = 'C.UTF-8'
    app_name = "{}-test-{}".format(os.path.basename(app_path), str(random.randint(0, 100000000)))
    __MODULE__.app_process = subprocess.Popen([app_path, '--name', app_name], env=os.environ)
    desktop = Atspi.get_desktop(0)

    __MODULE__.app_obj = None
    for t in range(0, stubbornness):
        for i in range(0, desktop.get_child_count()):
            app = desktop.get_child_at_index(i)
            if (app is not None) and (app.get_name() == app_name):
                __MODULE__.app_obj = app
                break
        if (__MODULE__.app_obj is not None):
            break
        time.sleep(0.5)

def stop():
    __MODULE__.app_process.kill()
    __MODULE__.app_process = None
    __MODULE__.app_obj = None




def onWidget(selector):
    assert __MODULE__.app_process is not None, "App is not initialized"
    assert __MODULE__.app_process.poll() is None, "The application no longer exists"
    assert __MODULE__.app_obj is not None, "Damn! I have no Atspi object for the app"

    assert type(selector) is str, "Bad selector"

    pred = _selector_pred(selector)
    obj = None
    try:
        obj = next((obj for obj in _tree_traversal(__MODULE__.app_obj) if pred(obj)))
    except StopIteration:
        obj = None
    if (obj is None):
        raise Exception("No widget matches: {}".format(selector))
    return obj


def _selector_pred(selector):
    if (selector[0] is "#"):
        name = selector[1:]
        return lambda obj: obj.get_name() == name
    if (selector.isupper()):
        try:
            role = Atspi.Role.__dict__[selector]
        except KeyError:
            raise Exception("Atspi does not include role {} ".format(selector))
        return lambda obj: obj.get_role() == role
    else:
        raise Exception("Selector {} not implemented".format(selector))



def _tree_traversal(parent):
    yield parent
    for i in range(0, parent.get_child_count()):
        child = parent.get_child_at_index(i)
        if (child.get_child_count() > 0):
            yield from _tree_traversal(child)
        else:
            yield child


# Creates function performing action named 'name'
# returns function
def perform(name):
    def perform_action_on(at_obj):
        iface = at_obj.get_action_iface()
        for i in range(0, iface.get_n_actions()):
            if (iface.get_action_name(i) == name):
                iface.do_action(i)
                return at_obj
            raise Exception("Widget {} has no action named {}".format(at_obj.get_name(), name))
    return perform_action_on
