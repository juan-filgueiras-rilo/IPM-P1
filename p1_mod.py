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

    def on_button_add_clicked(self, widget):
        data = self._view.run_dialog_add_edit("Añadir tarea", widget.get_toplevel())
        task_id = self._model.add(data)
        if task_id != -1:
            self._view.add(task_id,data)

    def on_button_edit_clicked(self, widget):
        task = self._view.get_task()
        if task != None:
            data = self._view.run_dialog_add_edit("Editar tarea", widget.get_toplevel(),task)
            if data != None:
                ok = self._model.edit(task[0],data)
                if ok != -1:
                    self._view.edit(task[0],data)
            
    def on_button_remove_clicked(self, widget):
        task = self._view.get_task()
        if task != None:
            ok = self._model.remove(task[0])
            if ok != -1:
                self._view.remove(task[0])

    def on_button_exit_clicked(self, widget):
        self._view.exit(widget)

'''
Vista
'''

class TaskList_View:
    def __init__(self):
        
        def date_cell_data_func(column, renderer, model, treeiter, data):
            fecha = model[treeiter][2]
            renderer.set_property('text', fecha.strftime("%x"))

        def compare_date(model, treeiter1, treeiter2, user_data):
            if model[treeiter1][2] < model[treeiter2][2]:
                return -1
            if model[treeiter1][2] > model[treeiter2][2]:
                return 1
            return 0

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
        self.store = Gtk.ListStore(int, str, GObject.TYPE_PYOBJECT, bool)
        self.store.append([100,"Llevar coche al taller", date.today(), False])
        self.store.append([101,"Lavar el coche", date(2017, 8, 1), False])
        self.store.append([102,"Pagar el seguro", date(2017,1,1), False])
        self.store.append([103,"Arreglar mando garaje", date.today(), False])
        self.store.append([104,"Recoger ropa del tinte", date.today(), False])
        self.store.append([105,"Regalo cumpleaños Nico", date(2018,1,1), False])
        self.store.append([106,"Devolver libro a la biblioteca", date(2018,2,12), True])
        self.store.append([107,"Ordenar el congelador", date(2017,9,12), False])
        self.store.append([108,"Lavar las cortinas", date(2017,10,1), False])
        self.store.append([109,"Organizar el cajón de los mandos", date(2017,10,5), False])
        self.store.append([110,"Poner flores en las jardineras", date.today(), False])

        #se crea un treeview sobre la lista store
        self.tree = Gtk.TreeView(self.store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tarea", renderer, text=1)
        self.tree.append_column(column)
        column.set_sort_column_id(1)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Fecha", renderer)
        column.set_cell_data_func(renderer, date_cell_data_func)
        self.tree.append_column(column)
        column.set_sort_column_id(2)
        self.store.set_sort_func(2, compare_date, None)
        renderer = Gtk.CellRendererToggle()
        column = Gtk.TreeViewColumn("Hecho", renderer, active=3)
        self.tree.append_column(column)
        box.pack_end(self.tree, True, True, 0)
        column.set_sort_column_id(3)

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

    def connect(self, controller):
        self._exit_button.connect('clicked', controller.on_button_exit_clicked)
        self._add_button.connect('clicked', controller.on_button_add_clicked)
        self._delete_button.connect('clicked', controller.on_button_remove_clicked)
        self._edit_button.connect('clicked', controller.on_button_edit_clicked)    

    def run_dialog_add_edit(self, title, parent, data=None):
        dialog = Gtk.Dialog(title, parent, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dialog.get_content_area()
        grid = Gtk.Grid()
        tareaEntry = Gtk.Entry()
        fechaEntry = Gtk.Entry()
        hechoCheckButton = Gtk.CheckButton("Hecho")
        if data != None:
            tareaEntry.set_text(data[1])
            fechaEntry.set_text(data[2].strftime("%x"))
            hechoCheckButton.set_active(data[3])
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

    def get_task(self):
        task = None
        selection = self.tree.get_selection()
        treeiter = selection.get_selected()[1]
        if treeiter != None:
            task = self.store.get(treeiter,0,1,2,3)
        return task

    def exit(self,widget):
        dialog = Gtk.MessageDialog(widget.get_toplevel(), 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "¿ Quieres detener esta acción ?")
        dialog.format_secondary_text("Si no la detienes, el programa terminará")
        dialog.run()
        dialog.destroy()
        Gtk.main_quit()

    def add(self, task_id, data):
        data = list(data)
        data.insert(0,task_id)
        data = tuple(data)
        self.store.append(data)

    def edit(self, task_id, data):
        for task in self.store:
            if task[0] == task_id:
                self.store.set(task.iter, 1, data[0], 2, data[1], 3, data[2])

    def remove(self, task_id):
        for task in self.store:
            if task[0] == task_id:
                self.store.remove(task.iter)
                return


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
        self.ID = 0
        self.model_task_list = []
        self.model_task_list.append([100,"Llevar coche al taller", date.today(), False])
        self.model_task_list.append([101,"Lavar el coche", date(2017, 8, 1), False])
        self.model_task_list.append([102,"Pagar el seguro", date(2017,1,1), False])
        self.model_task_list.append([103,"Arreglar mando garaje", date.today(), False])
        self.model_task_list.append([104,"Recoger ropa del tinte", date.today(), False])
        self.model_task_list.append([105,"Regalo cumpleaños Nico", date(2018,1,1), False])
        self.model_task_list.append([106,"Devolver libro a la biblioteca", date(2018,2,12), True])
        self.model_task_list.append([107,"Ordenar el congelador", date(2017,9,12), False])
        self.model_task_list.append([108,"Lavar las cortinas", date(2017,10,1), False])
        self.model_task_list.append([109,"Organizar el cajón de los mandos", date(2017,10,5), False])
        self.model_task_list.append([110,"Poner flores en las jardineras", date.today(), False])

    #
    ##   add asigna un ID de tarea único a la lista de 
    ##   tareas y la concatena en la lista del modelo devolviendo el ID
    ##   Si la informacion es nula, simplemente devuelve -1 a modo de error
    #

    def add(self, data):
        done = -1
        if data != None:
            data = list(data)
            data.insert(0, self.ID)
            data = tuple(data)
            self.model_task_list.append(data)
            done = self.ID
            self.ID += 1
        return done

    def edit(self, task_id, data):
        done = -1
        #cojo el ID para buscar si está ese elemento en la lista
        for task in self.model_task_list:
            if task_id == task[0]:
                task = (task_id, data[0], data[1], data[2])
                print(task)
                done = task_id
                break
        return done

    def remove(self, task_id):
        done = -1
        for task in self.model_task_list:
            if (task_id == task[0]):
                done = task_id
                self.model_task_list.remove(task)
                break
        return done

if __name__ == '__main__':

    # Workarround para el control-c https://bugzilla.gnome.org/show_bug.cgi?id=622084#c4
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    TaskList_Controller().set_model(TaskList_Model())
    Gtk.main()
