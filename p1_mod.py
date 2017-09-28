#!/usr/bin/env python3

""" Código base para la práctica de IPM. Existen numerosos fallos de diseño que deben ser corregidos."""

__author__     = "Guillermo Martín Villar, Juan Luis Filgueiras Rilo"
__copyright__  = "GNU General Public Licencse v2"


from datetime import datetime, date

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject

'''
Controlador
'''

class TaskList_Controller:

    def __init__(self):
        self._view = TaskList_View()
        self._view.connect(self)


    def set_model(self, model):
        self._model = model

    def on_button_añadir_clicked(self, widget, tree):
        data = self._view.run_dialog_añadir_editar("Añadir tarea", widget.get_toplevel())
        if data != None:
            tree.get_model().append(data)

    def on_button_editar_clicked(self, widget, tree):
        selection = tree.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter != None:
            data = self._view.run_dialog_añadir_editar("Editar tarea", widget.get_toplevel(), model[treeiter])
            if data != None:
                model.set(treeiter, 0, data[0])
                model.set(treeiter, 1, data[1])
                model.set(treeiter, 2, data[2])
            
    def on_button_eliminar_clicked(self, widget, tree):
        selection = tree.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter != None:
            model.remove(treeiter) 

    def on_button_salir_clicked(self, widget):
        #self._view.run_dialog()?
        dialog = Gtk.MessageDialog(widget.get_toplevel(), 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "¿ Quieres detener esta acción ?")
        dialog.format_secondary_text("Si no la detienes, el programa terminará")
        dialog.run()
        dialog.destroy()
        Gtk.main_quit()

'''
Vista
'''

class TaskList_View:
    def __init__(self):
        self._win = Gtk.Window(title="Práctica 1 -- IPM 17/18")
        self._win.connect("delete-event", Gtk.main_quit)
        
        # El código sigue los ejemplos del tuto: https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._win.add(box)
        
        #
        # # 
        #
        
        self._exit_button = Gtk.Button(label="Salir")
        box.pack_end(self._exit_button, True, True, 0)

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

        self.tree = Gtk.TreeView(store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tarea", renderer, text=0)
        self.tree.append_column(column)
        column.set_sort_column_id(0)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Fecha", renderer)
        column.set_cell_data_func(renderer, fecha_cell_data_func)
        self.tree.append_column(column)
        column.set_sort_column_id(1)
        store.set_sort_func(1, compare_fecha, None)
        renderer = Gtk.CellRendererToggle()
        column = Gtk.TreeViewColumn("Hecho", renderer, active=2)
        self.tree.append_column(column)
        box.pack_end(self.tree, True, True, 0)
        column.set_sort_column_id(2)

        #
        # #
        #

        box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.pack_start(box2, True, True, 0)

        self._add_button = Gtk.Button(label="Añadir")
        box2.pack_end(self._add_button, True, True, 0)

        self._delete_button = Gtk.Button(label="Eliminar")
        box2.pack_end(self._delete_button, True, True, 0)

        self._edit_button = Gtk.Button(label="Editar")
        box2.pack_end(self._edit_button, True, True, 0)
        #GLib.idle_add(welcome, self._win)
        self._win.show_all()

    def run_dialog_añadir_editar(self, title, parent, data=None):
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

    def connect(self, controller):
        self._exit_button.connect('clicked', controller.on_button_salir_clicked)
        self._add_button.connect('clicked', controller.on_button_añadir_clicked, self.tree)
        self._delete_button.connect('clicked', controller.on_button_eliminar_clicked, self.tree)
        self._edit_button.connect('clicked', controller.on_button_editar_clicked, self.tree)


    # def welcome(window):
    #     welcome = Gtk.Dialog("El mítico gestor de tareas", window, 0, 
    #                          (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
    #                           Gtk.STOCK_OK, Gtk.ResponseType.OK))
    #     vbox = Gtk.VBox(spacing = 10)
    #     welcome.get_content_area().add(vbox)
                    
    #     etiqueta1 = Gtk.Label("Bienvenido !!!!!111!!!")

    #     etiqueta2 = Gtk.Label("(╯◕_◕)╯ (╯◕_◕)╯ ╰(◣﹏◢)╯ ╰(◕_◕╰) ╰(◕_◕╰)")
    #     vbox.pack_start(etiqueta1, True, True, 0)
    #     vbox.pack_start(etiqueta2, True, True, 0)
    #     welcome.show_all()
    #     respuesta = welcome.run()
                    
    #     if respuesta == Gtk.ResponseType.OK:
    #         welcome.destroy()
    #         win.show_all()
    #     elif respuesta == Gtk.ResponseType.CANCEL:
    #         welcome.destroy()
    #         Gtk.main_quit()

'''
Modelo
'''

class TaskList_Model:
    def __init__(self):
        pass

'''
A clasificar
'''        
    
def fecha_cell_data_func(column, renderer, model, treeiter, data):
       fecha = model[treeiter][1]
       renderer.set_property('text', fecha.strftime("%x"))


def compare_fecha(model, treeiter1, treeiter2, user_data):
    if model[treeiter1][1] < model[treeiter2][1]:
        return -1
    if model[treeiter1][1] > model[treeiter2][1]:
        return 1
    return 0

if __name__ == '__main__':

    # Workarround para el control-c https://bugzilla.gnome.org/show_bug.cgi?id=622084#c4
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    TaskList_Controller().set_model(TaskList_Model())
    Gtk.main()
