#!/usr/bin/env python3

""" Código base para la práctica de IPM. Existen numerosos fallos de diseño que deben ser corregidos."""

__author__     = "Guillermo Martín Villar, Juan Luis Filgueiras Rilo"
__copyright__  = "GNU General Public Licencse v2"


from datetime import datetime, date, time

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

	#llamamos al metodo que muestra las cajas en la vista
	def on_button_add_clicked(self, widget):
		self._view.run_dialog_add()

	def on_button_remove_clicked(self, widget):
		task = self._view.get_task()
		if task != None:
			ok = self._model.remove(task[0])
			if ok != -1:
				self._view.remove(task[0])

	def on_button_exit_clicked(self, widget, event):
		signal = self._view.exit(widget.get_toplevel())
		return signal

	#metodo que se lanza al editar la columna fecha de una tarea
	def on_task_date_edit(self, widget, position, text):
		date = self._model.convert_string_to_datetime(text)
		if (date == (None,"void-date")):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
					"Date is empty")
		elif (date == (None,"bad-format")):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
					"Provided data is not in the correct form (dd/mm/yy)")
		elif (date == (None,"prior-date")):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
					"Provided date must be subsequent to the current date")
		else:
			task = self._view.get_task()
			if (task != None):
				task = list(task)
				#convertirmos a datetime el string que introduce el usuario
				task[2] = date[0]
				task = tuple(task)
				data = (task[1], task[2], task[3])
				ok = self._model.edit(task[0], data)
				if ok != -1:
					self._view.edit(task[0], data)

	#metodo que se lanza al editar la columna nombre de una tarea
	def on_task_name_edit(self, widget, position, text):
		#pasamos la cuadrupla a lista, editamos el valor y lo editamos en modelo
		#si todo ok, lo editamos en la vista tambien
		#si el string pasado por el usuario no es valido, ya no se hace nada mas
		if not (self._model.validate_taskname(text)):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
				"Task name should not be empty")
		else:
			task = self._view.get_task()
			if (task != None):
				task = list(task)
				task[1] = text
				task = tuple(task)
				data = (task[1], task[2], task[3])
				ok = self._model.edit(task[0], data)
				if ok != -1:
					self._view.edit(task[0], data)

	#metodo que se lanza al seleccionar la columna hecho        
	def on_row_selected(self, widget, position, n_column):
		if (n_column.get_title() == "Hecho"):
			task = self._view.get_task()
			#convertimos a lista y despues reconvertimos a tupla pq las tuplas son
			#inmutables
			task = list(task)
			#haciendolo ternaria, queda mas chulo
			task[3] = False if task[3] else True
			task = tuple(task)
			data = (task[1], task[2], task[3])
			ok = self._model.edit(task[0], data)
			if ok != -1:
				self._view.edit(task[0], data)
		else:
			self._view.update_state(True)

	#metodo que se lanza al añadir una nueva tarea
	def on_button_add_task_clicked(self, widget):
		data = self._view.run_dialog_add_prueba()
		data = list(data)
		date = self._model.convert_string_to_datetime(data[1])
		if (date == (None,"void-date")):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
					"Date is empty")
		elif (date == (None,"bad-format")):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
					"Provided data is not in the correct form (dd/mm/yy)")
		elif (date == (None,"prior-date")):
			self._view.run_dialog_provided_data_error("CRITICAL ERROR",
					"Provided date must be subsequent to the current date")
		else:
			data[1] = date[0]
			if not (self._model.validate_taskname(data[0])):
				self._view.run_dialog_provided_data_error("CRITICAL ERROR",
				"Task name should not be empty")
			else:
				data = tuple(data)
				task_id = self._model.add(data)
				if task_id != -1:
					self._view.add(task_id,data)

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
		# El código sigue los ejemplos del tuto: https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

		#metemos los entrys en una caja nueva por el final
		self.hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		
		self.tareaEntry = Gtk.Entry()
		self.fechaEntry = Gtk.Entry()

		self.hbox1.pack_start(self.tareaEntry, True, True, 0)
		


		#pendiente de cuadrar mejor
		#metemos los labels en una caja imnediatamente encima de la anterior
		self.hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 8)
		name_label = Gtk.Label("Nombre de tarea")
		name_label.set_xalign(0)
		name_label.set_max_width_chars(1)
		self.hbox2.pack_start(name_label, True, True, 0)

		date_label = Gtk.Label("Fecha")
		date_label.set_xalign(0)
		self.hbox2.pack_start(date_label, True, True, 0)
		
		self.add_task_button = Gtk.Button(label="+")
		#self.add_task_button.set_sensitive(False)
		#box2.pack_end(self._delete_button, True, True, 0)

		self.hbox1.pack_end(self.add_task_button, True, True, 0)
		self.hbox1.pack_end(self.fechaEntry, True, True, 0)
		box.pack_end(self.hbox1, True, True, 0)
		box.pack_end(self.hbox2, True, True, 0)
		

		self._win.add(box)
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
		#activamos que la activación de una fila se produzca en un simple click en vez 
		#de doble click
		self.tree.set_activate_on_single_click(True)
		#diferenciamos entre el renderer del nombre y de la fecha pq a la hora de editar
		#seran eventos diferentes
		self.renderer_name = Gtk.CellRendererText()
		#marcamos la columna entera como editable
		self.renderer_name.set_property("editable", True)
		column = Gtk.TreeViewColumn("Tarea", self.renderer_name, text=1)
		self.tree.append_column(column)
		column.set_sort_column_id(1)
		self.renderer_date = Gtk.CellRendererText()
		#marcamos la columna entera como editable
		self.renderer_date.set_property("editable", True)
		column = Gtk.TreeViewColumn("Fecha", self.renderer_date)
		column.set_cell_data_func(self.renderer_date, date_cell_data_func)
		self.tree.append_column(column)
		column.set_sort_column_id(2)
		self.store.set_sort_func(2, compare_date, None)
		renderer_make = Gtk.CellRendererToggle()
		column = Gtk.TreeViewColumn("Hecho", renderer_make, active=3)
		self.tree.append_column(column)
		box.pack_end(self.tree, True, True, 0)
		column.set_sort_column_id(3)

		#
		# #
		#


		box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		box.pack_start(box2, True, True, 0)

		self._add_button = Gtk.Button(label="Añadir")
		self._add_button.get_style_context().add_class('suggestive-action')
		box2.pack_end(self._add_button, True, True, 0)

		self._delete_button = Gtk.Button(label="Eliminar")
		self._delete_button.get_style_context().add_class('destructive-action')
		self._delete_button.set_sensitive(False)
		box2.pack_end(self._delete_button, True, True, 0)
		self._win.show_all()

		self.hbox1.hide()
		self.hbox2.hide()




	def connect(self, controller):
		#self._exit_button.connect('clicked', controller.on_button_exit_clicked)
		self._win.connect("delete-event", controller.on_button_exit_clicked)
		self._add_button.connect('clicked', controller.on_button_add_clicked)
		self._delete_button.connect('clicked', controller.on_button_remove_clicked)
		self.tree.connect('row-activated', controller.on_row_selected)
		#editar el nombre de la tarea
		self.renderer_name.connect('edited', controller.on_task_name_edit)
		#editar la fecha de la tarea
		self.renderer_date.connect('edited', controller.on_task_date_edit)
		self.add_task_button.connect('clicked', controller.on_button_add_task_clicked)



	#metodo con el que mostramos las dos cajas del fondo
	def run_dialog_add(self):
		self.hbox1.show_all()
		self.hbox2.show_all()
		

	#metodo con el que añadimos la tarea a la vista y al modelo
	def run_dialog_add_prueba(self):
		data = (self.tareaEntry.get_text(), self.fechaEntry.get_text(),False)
		self.tareaEntry.set_text("")
		self.fechaEntry.set_text("")
		self.hbox1.hide()
		self.hbox2.hide()
		return data
		
	def run_dialog_provided_data_error(self, title, secondary_text):
		dialog = Gtk.MessageDialog(self._win, 0, 
			Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
			title)
		dialog.format_secondary_text(secondary_text)
		dialog.run()
		dialog.destroy()

	def get_task(self):
		task = None
		selection = self.tree.get_selection()
		treeiter = selection.get_selected()[1]
		if treeiter != None:
			task = self.store.get(treeiter,0,1,2,3)
		return task

	def exit(self, parent):
		dialog = Gtk.Dialog("WARNING", parent, Gtk.DialogFlags.DESTROY_WITH_PARENT, 
				(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
				Gtk.STOCK_OK, Gtk.ResponseType.OK))
		vbox = Gtk.VBox(spacing = 10)
		dialog.get_content_area().add(vbox)
					
		etiqueta1 = Gtk.Label("Do you want to close application?")

		etiqueta2 = Gtk.Label("If you don't cancel, application will close")
		vbox.pack_start(etiqueta1, True, True, 0)
		vbox.pack_start(etiqueta2, True, True, 0)
		vbox.show_all()
		respuesta = dialog.run()
					
		if respuesta == Gtk.ResponseType.OK:
			Gtk.main_quit()
		else:
			dialog.destroy()
			return True

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
				
	def update_state(self, active):
		self._delete_button.set_sensitive(active)


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

	#metodo que valida el nombre de una tarea, devuelve True si el valor
	#introducido por parametro es valido y False en caso contrario
	def validate_taskname(self, name):
		if (name == ""):
			return False
		return True


	#metodo que valida la fecha de una tarea, devuelve True si el valor
	#introducido por parametro es valido y False en caso contrario
	def validate_taskdate(self, date):
		if not (datetime.now() < date):
			return False
		return True

	#metodo que intenta pasar un string a datetime, en caso de no poder, lanza un 
	#dialogo de error
	def convert_string_to_datetime(self, string_to_convert):
		if (string_to_convert == ""):
			return (None,"void-date")
		else:
			try:
				date = (datetime.strptime(string_to_convert, "%d/%m/%y"))
			except Exception:
				return (None,"bad-format")
			validate = self.validate_taskdate(date)
			if not (validate):
				return (None, "prior-date")
			else:
				return (date, "")

if __name__ == '__main__':

	# Workarround para el control-c https://bugzilla.gnome.org/show_bug.cgi?id=622084#c4
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	TaskList_Controller().set_model(TaskList_Model())
	Gtk.main()
