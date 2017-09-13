#!/usr/bin/env python3

""" Código base para la práctica de IPM. Existen numerosos fallos de diseño que deben ser corregidos."""

__author__     = "David Cabrero Souto"
__copyright__  = "GNU General Public Licencse v2"


from datetime import datetime, date

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject


def on_button_salir_clicked(widget):
    dialog = Gtk.MessageDialog(widget.get_toplevel(), 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "¿ Quieres detener esta acción ?")
    dialog.format_secondary_text("Si no la detienes, el programa terminará")
    dialog.run()
    dialog.destroy()
    Gtk.main_quit()


def run_dialog_añadir_editar(title, parent, data=None):
    dialog = Gtk.Dialog(title, parent, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
    box = dialog.get_content_area()
    grid = Gtk.Grid()
    tareaEntry = Gtk.Entry()
    fechaEntry = Gtk.Entry()
    hechoCheckButton = Gtk.CheckButton("Hecho")
    if data != None:
        tareaEntry.set_text(data[0])
        fechaEntry.set_text(data[1].strftime("%x"))
        hechoCheckButton.set_active(data[2])
    grid.attach(Gtk.Label("Tarea"), 0, 0, 1, 1)
    grid.attach(tareaEntry, 1, 0, 1, 1)
    grid.attach(Gtk.Label("Fecha"), 0, 1, 1, 1)
    grid.attach(fechaEntry, 1, 1, 1, 1)
    grid.attach(hechoCheckButton, 1, 2, 1, 1)
    box.pack_start(grid, True, True, 0)
    box.show_all()
    response = dialog.run()
    data = None
    if response == Gtk.ResponseType.OK:
        try:
            data = [tareaEntry.get_text(), datetime.strptime(fechaEntry.get_text(), "%x"), hechoCheckButton.get_active()]
        except ValueError:
            pass
    dialog.destroy()
    return data
    
def on_button_añadir_clicked(widget, tree):
    data = run_dialog_añadir_editar("Añadir tarea", widget.get_toplevel())
    if data != None:
        tree.get_model().append(data)


def on_button_editar_clicked(widget, tree):
    selection = tree.get_selection()
    model, treeiter = selection.get_selected()
    if treeiter != None:
        data = run_dialog_añadir_editar("Editar tarea", widget.get_toplevel(), model[treeiter])
        if data != None:
            model.set(treeiter, 0, data[0])
            model.set(treeiter, 1, data[1])
            model.set(treeiter, 2, data[2])
        
        
def on_button_eliminar_clicked(widget, tree):
    selection = tree.get_selection()
    model, treeiter = selection.get_selected()
    if treeiter != None:
        model.remove(treeiter)
        

def fecha_cell_data_func(column, renderer, model, treeiter, data):
    fecha = model[treeiter][1]
    renderer.set_property('text', fecha.strftime("%x"))


def compare_fecha(model, treeiter1, treeiter2, user_data):
    if model[treeiter1][1] < model[treeiter2][1]:
        return -1
    if model[treeiter1][1] > model[treeiter2][1]:
        return 1
    return 0


def welcome(window):
    welcome = Gtk.Dialog("El mítico gestor de tareas", window, 0, 
                         (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
    vbox = Gtk.VBox(spacing = 10)
    welcome.get_content_area().add(vbox)
                
    etiqueta1 = Gtk.Label("Bienvenido !!!!!111!!!")

    etiqueta2 = Gtk.Label("(╯◕_◕)╯ (╯◕_◕)╯ ╰(◣﹏◢)╯ ╰(◕_◕╰) ╰(◕_◕╰)")
    vbox.pack_start(etiqueta1, True, True, 0)
    vbox.pack_start(etiqueta2, True, True, 0)
    welcome.show_all()
    respuesta = welcome.run()
                
    if respuesta == Gtk.ResponseType.OK:
        welcome.destroy()
        win.show_all()
    elif respuesta == Gtk.ResponseType.CANCEL:
        welcome.destroy()
        Gtk.main_quit()


    
if __name__ == '__main__':

    # Workarround para el control-c https://bugzilla.gnome.org/show_bug.cgi?id=622084#c4
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    win = Gtk.Window(title="Práctica 1 -- IPM 17/18")
    win.connect("delete-event", Gtk.main_quit)
    
    # El código sigue los ejemplos del tuto: https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html
    
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    win.add(box)

    #
    # #
    #
    
    button = Gtk.Button(label="Salir")
    button.connect('clicked', on_button_salir_clicked)
    box.pack_end(button, True, True, 0)

    #
    # #
    #
    
    store = Gtk.ListStore(str, GObject.TYPE_PYOBJECT, bool)
    store.append(["Llevar coche al taller", date.today(), False])
    store.append(["Lavar el coche", date(2017, 8, 1), False])
    store.append(["Pagar el seguro", date(2017,1,1), False])
    store.append(["Arreglar mando garaje", date.today(), False])
    store.append(["Recoger ropa del tinte", date.today(), False])
    store.append(["Regalo cumpleaños Nico", date(2018,1,1), False])
    store.append(["Devolver libro a la biblioteca", date(2018,2,12), True])
    store.append(["Ordenar el congelador", date(2017,9,12), False])
    store.append(["Lavar las cortinas", date(2017,10,1), False])
    store.append(["Organizar el cajón de los mandos", date(2017,10,5), False])
    store.append(["Poner flores en las jardineras", date.today(), False])

    tree = Gtk.TreeView(store)
    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Tarea", renderer, text=0)
    tree.append_column(column)
    column.set_sort_column_id(0)
    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Fecha", renderer)
    column.set_cell_data_func(renderer, fecha_cell_data_func)
    tree.append_column(column)
    column.set_sort_column_id(1)
    store.set_sort_func(1, compare_fecha, None)
    renderer = Gtk.CellRendererToggle()
    column = Gtk.TreeViewColumn("Hecho", renderer, active=2)
    tree.append_column(column)
    box.pack_end(tree, True, True, 0)
    column.set_sort_column_id(2)

    #
    # #
    #

    box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    box.pack_start(box2, True, True, 0)

    button = Gtk.Button(label="Añadir")
    button.connect('clicked', on_button_añadir_clicked, tree)
    box2.pack_end(button, True, True, 0)

    button = Gtk.Button(label="Eliminar")
    button.connect('clicked', on_button_eliminar_clicked, tree)
    box2.pack_end(button, True, True, 0)

    button = Gtk.Button(label="Editar")
    button.connect('clicked', on_button_editar_clicked, tree)
    box2.pack_end(button, True, True, 0)

    #
    # #
    #

    GLib.idle_add(welcome, win)
    
    Gtk.main()
