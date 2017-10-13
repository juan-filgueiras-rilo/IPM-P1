#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Código base para la práctica de IPM. Existen numerosos fallos de diseño que deben ser corregidos."""

__author__     = "Guillermo Martín Villar, Juan Luis Filgueiras Rilo"
__copyright__  = "GNU General Public Licencse v2"


from datetime import datetime, date, time

import time

import threading

from random import randint

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject


#internacionalización
import gettext 
import locale 

LOCALE_DIR = './locale' 
APP_NAME = 'p1_mod' 


gettext.textdomain(APP_NAME)
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
locale.setlocale(locale.LC_ALL, '') 
_ = gettext.gettext


_DATE_FORMAT = _("%d/%m/%y")
#Cabecera
#Notificaciones
'''
Controlador
'''

class TaskList_Controller:

	INITIAL_STATE = {'spinner_running': False,
					'sync_button': True,
					'sync_status': _("Última sincronización: Aún no se ha sincronizado")}

	def __init__(self):
		self._view = TaskList_View()
		self._view.update_state(self.INITIAL_STATE)
		self._view.connect(self)

	def set_model(self, model):
		self._model = model

	#llamamos al metodo que muestra las cajas en la vista
	def on_button_add_clicked(self, widget):
		self._view.update_add(False)
		self._view.run_dialog_add()

	def remove_task(self, task):
		if (task != None):
			ok = self._model.remove(task[0])
			if (ok != -1):
				self._view.remove(task[0])
				self._view.remove_selection()
		self._view.update_menu_options()

	def on_button_remove_clicked(self, widget):
		tasklist = self._view.get_tasks()
		for task in tasklist:
			self.remove_task(task)



	def on_button_exit_clicked(self, widget, event):
		signal = self._view.exit(widget.get_toplevel())
		return signal

	#metodo que se lanza al editar la columna fecha de una tarea
	def on_task_date_edit(self, widget, position, text):
		date = self._model.convert_string_to_datetime(text)
		if (date == (None,"void-date")):
			self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("La fecha está vacía"))
		elif (date == (None,"bad-format")):
			self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("La fecha introducida no está en el formato correcto (dd/mm/yy)"))
		elif (date == (None,"prior-date")):
			self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("La fecha introducida tiene que ser posterior a la fecha actual"))
		else:
			#task = self._view.get_task()
			task = self._view.get_tasks()[0]
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
		tasklist = self._view.get_tasks()
		if ((len(tasklist)) != 0):
			if not (self._model.validate_taskname(text)):
				self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("El nombre de la tarea no puede estar vacío"))
			else:
				#task = self._view.get_task()
				task = self._view.get_tasks()[0]
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
		if (n_column.get_title() == _("Hecho")):
			#task = self._view.get_task()
			task = self._view.get_tasks()[0]
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
				self._view.update_menu_options()
		# else:
		# 	self._view.update_delete(True)

	#metodo que se lanza al añadir una nueva tarea
	def on_button_add_task_clicked(self, widget):
		data = self._view.run_dialog_add_prueba()
		data = list(data)
		date = self._model.convert_string_to_datetime(data[1])
		if (date == (None,"void-date")):
			self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("La fecha está vacía"))
		elif (date == (None,"bad-format")):
			self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("La fecha introducida no está en el formato correcto (dd/mm/yy)"))
		elif (date == (None,"prior-date")):
			self._view.run_dialog_provided_data_error(_("Error Crítico"),
					_("La fecha introducida tiene que ser posterior a la fecha actual"))
		else:
			data[1] = date[0]
			if not (self._model.validate_taskname(data[0])):
				self._view.run_dialog_provided_data_error(_("Error Crítico"),
				_("El nombre de la tarea no puede estar vacío"))
			else:
				data = tuple(data)
				task_id = self._model.add(data)
				if task_id != -1:
					self._view.remove_entry_text()
					self._view.update_add(True)
					self._view.update_add_task(False)
					self._view.add(task_id,data)
					self._view.update_menu_options()

	def on_button_sync_clicked(self, widget):
		prev_status = self._view._sync_label.get_text()

		state = {'spinner_running' : True,
				'sync_button' : False,
				'sync_status' : _("Sincronizando"+'\u2026')}
		self._view.update_state(state)
		t = threading.Thread(target = self.sync, args = (prev_status, ))
		t.start()

	def sync(self, prev_status):
		sync_success = self._model.sync()
		if sync_success:
			state = {'spinner_running' : False,
					'sync_button' : True,
					'sync_status' : _("Última sincronización: ") + time.strftime("%H:%M")}
		else:
			state =  {'spinner_running' : False,
					'sync_button' : True,
					'sync_status' : prev_status,
					'show_sync_error' : _("Error Sincronizando")}
		self._view.update_state_on_main_thread(state)

	def on_key_pressed(self, entry, eventkey):
		#se añade la tarea al pulsar la tecla enter solo si hay buffer en ambos entrys
		if ((eventkey.get_keyval()[1] == 65293) 
				& (self._view.get_name_buffer_has_text()) 
				& (self._view.get_date_buffer_has_text())):
			self.on_button_add_task_clicked(entry)	

	def on_tarea_entry_changed(self, entry):
		length = entry.get_buffer().get_length()
		if (length > 0):
			self._view.update_name_buffer(True)
		else:
			self._view.update_name_buffer(False)

	def on_fecha_entry_changed(self, entry):
		length = entry.get_buffer().get_length()
		if (length > 0):
			self._view.update_date_buffer(True)
		else:
			self._view.update_date_buffer(False)

	def on_supr_pressed(self, entry, eventkey):
		if ((eventkey.get_keyval()[1] == 65535)):
			self.on_button_remove_clicked(entry)


	def on_focus_out_treeview(self, uno, dos):
		# print("Hola") 
		# print(uno)
		# print(dos)
		self._view.update_delete(False)

	

	def on_delete_all_clicked(self, menuitem):
		task_list = self._view.get_task_list()
		for task in task_list:
			self.remove_task(task)

	def on_delete_all_done_clicked(self, menuitem):
		task_list = self._view.get_task_list()
		for task in task_list:
			if (task[3]):
				self.remove_task(task)

	def on_tree_selection_changed(self, widget):
		self._view.update_delete(True)

		
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
			
		self._win = Gtk.Window(title=_("Práctica 1" + '\u2013' +  "IPM 17/18"))
		self._win.set_size_request(500, 500)
		# El código sigue los ejemplos del tuto: https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html
		header_bar = Gtk.HeaderBar()
		header_bar.set_show_close_button(True)
		header_bar.props.title = _("Práctica 1" + '\u2013' +  "IPM 17/18")
		self._win.set_titlebar(header_bar)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		# box.pack_start(header_bar, True, True, 0)




		

		self._win.add(box)
		self.store = Gtk.ListStore(int, str, GObject.TYPE_PYOBJECT, bool)
		self.store
		self.store.append([100,"Llevar coche al taller", datetime.today(), False])
		self.store.append([101,"Lavar el coche", datetime(2017, 8, 1), False])
		self.store.append([102,"Pagar el seguro", datetime(2017,1,1), False])
		self.store.append([103,"Arreglar mando garaje", datetime.today(), False])
		self.store.append([104,"Recoger ropa del tinte", datetime.today(), False])
		self.store.append([105,"Regalo cumpleaños Nico", datetime(2018,1,1), False])
		self.store.append([106,"Devolver libro a la biblioteca", datetime(2018,2,12), True])
		self.store.append([107,"Ordenar el congelador", datetime(2017,9,17), False])
		self.store.append([108,"Lavar las cortinas", datetime(2017,10,1), False])
		self.store.append([109,"Organizar el cajón de los mandos", datetime(2017,10,5), False])
		self.store.append([110,"Poner flores en las jardineras", datetime.today(), False])

		#se crea un treeview sobre la lista store
		self.tree = Gtk.TreeView(self.store)
		#activamos que la activación de una fila se produzca en un simple click en vez 
		#de doble click
		self.tree.set_activate_on_single_click(True)
		self.selection = self.tree.get_selection()


		#seleccion multiple
		self.tree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
		self.tree.set_rubber_banding(True)
		
		#diferenciamos entre el renderer del nombre y de la fecha pq a la hora de editar
		#seran eventos diferentes
		self.renderer_name = Gtk.CellRendererText()
		#marcamos la columna entera como editable
		self.renderer_name.set_property("editable", True)
		#centramos el texto que irá dentro de la columna
		self.renderer_name.set_alignment(0.5, 0)
		column = Gtk.TreeViewColumn(_("Tarea"), self.renderer_name, text=1)
		#permitimos que la columna se pueda expandir
		column.set_expand(True)
		#centramos el texto del título de la columna
		column.set_alignment(0.5)
		self.tree.append_column(column)
		column.set_sort_column_id(1)
		self.renderer_date = Gtk.CellRendererText()
		#marcamos la columna entera como editable
		self.renderer_date.set_property("editable", True)
		#centramos el texto que irá dentro de la columna
		self.renderer_date.set_alignment(0.5, 0)
		column = Gtk.TreeViewColumn(_("Fecha"), self.renderer_date)
		#permitimos que la columna se pueda expandir
		column.set_expand(True)
		#centramos el texto del título de la columna
		column.set_alignment(0.5)
		column.set_cell_data_func(self.renderer_date, date_cell_data_func)
		self.tree.append_column(column)
		column.set_sort_column_id(2)
		self.store.set_sort_func(2, compare_date, None)
		renderer_make = Gtk.CellRendererToggle()
		column = Gtk.TreeViewColumn(_("Hecho"), renderer_make, active=3)
		#permitimos que la columna se pueda expandir
		column.set_expand(True)
		#centramos el texto del título de la columna
		column.set_alignment(0.5)
		self.tree.append_column(column)
		#self.tree.set_headers_visible(False)
		column.set_sort_column_id(3)


		#barra superior

		#creamos los elementos
		#botón de añadir
		self._add_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_ADD,1)
		self._add_button.get_style_context().add_class('suggestive-action')
		self._delete_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_REMOVE,1)
		self._delete_button.get_style_context().add_class('destructive-action')
		self._delete_button.set_sensitive(False)
		self._sync_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_REFRESH,1)
		self._sync_button.set_alignment(1,0)
		self.menu_button = Gtk.MenuButton()

		self.menu = Gtk.Menu()
		self.delete_all = Gtk.MenuItem(_("Borrar todo"))
		self.delete_all.show()
		self.delete_done_tasks = Gtk.MenuItem(_("Borrar tareas hechas"))
		self.delete_done_tasks.show()
		# self.menu.attach(delete_all, 0, 1, 2, 3)
		# self.menu.attach(delete_done_tasks, 1, 1, 1, 1)
		self.menu.append(self.delete_all)
		self.menu.append(self.delete_done_tasks)
		self.menu_button.set_popup(self.menu)
		self.delete_all.set_sensitive(False)







		#espacio donde irá el sync label y sync spinner
		box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		self.sync_spinner = Gtk.Spinner()
		self._sync_label = Gtk.Label("")
		#lo alineamos casi abajo del todo
		self._sync_label.set_alignment(0.5, 0.8)
		#dejamos un poco de espacio por arriba y por abajo para que no
		#se vea tan pequeño
		self._sync_label.set_size_request(0, 30)
		


		#diálogo añadir
		#metemos los entrys en una caja nueva por el final
		#self.hbox_add_dialog1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		self.tareaEntry = Gtk.Entry()
		self.fechaEntry = Gtk.Entry()
		#pendiente de cuadrar mejor
		#metemos los labels en una caja imnediatamente encima de la anterior
		#self.hbox_add_dialog2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 8)
		name_label = Gtk.Label(_("Nombre"))
		name_label.set_xalign(1)
		name_label.set_max_width_chars(1)
		date_label = Gtk.Label(_("Fecha"))
		date_label.set_xalign(1)
		self.add_task_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_ADD,1)
		self.add_task_button.set_sensitive(False)
		self.add_task_button.set_alignment(0.5, 0.5)


		self.hbox_add_dialog = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 0)
		self.vbox_add_dialog1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
		self.vbox_add_dialog2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
		self.vbox_add_dialog3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 8)


		#lo metemos todo en sus respectivas cajas

		self.vbox_add_dialog1.pack_start(name_label, True, True, 0)
		self.vbox_add_dialog1.pack_end(date_label, True, True, 0)
		self.vbox_add_dialog2.pack_start(self.tareaEntry, True, True, 0)
		self.vbox_add_dialog2.pack_end(self.fechaEntry, True, True, 0)
		#espacio que irá entre los bordes de la caja y el botón (arriba y abajo)
		self.vbox_add_dialog3.pack_start(self.add_task_button, True, True, 8)
		#espacio que irá entre los border de la caja y la caja que metemos a izquierda y derecha
		self.hbox_add_dialog.pack_start(self.vbox_add_dialog1, True, True, 18)
		self.hbox_add_dialog.pack_start(self.vbox_add_dialog2, True, True, 0)
		#espacio que irá entre los border de la caja y la caja que metemos a izquierda y derecha
		self.hbox_add_dialog.pack_end(self.vbox_add_dialog3, True, True, 18)

		#espacio que irá entre los border de la caja y la caja que metemos arriba y abajo
		box.pack_end(self.hbox_add_dialog, False, False, 18)


		box.pack_end(self.tree, True, True, 0)
		box2.pack_start(self.sync_spinner, False, False, 0)
		box2.pack_start(self._sync_label, True, True, 0)
		header_bar.pack_start(self.menu_button)
		header_bar.pack_end(self._add_button)
		header_bar.pack_end(self._delete_button)
		header_bar.pack_end(self._sync_button)
		box.pack_start(box2, False, False, 0)

		self._win.show_all()
		self.hbox_add_dialog.hide()

		self.name_buffer_has_text = False
		self.date_buffer_has_text = False
		self.update_menu_options()

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
		self._sync_button.connect('clicked', controller.on_button_sync_clicked)
		self.tareaEntry.connect('key-press-event', controller.on_key_pressed)
		self.fechaEntry.connect('key-press-event', controller.on_key_pressed)
		self.tareaEntry.connect('changed', controller.on_tarea_entry_changed)
		self.fechaEntry.connect('changed', controller.on_fecha_entry_changed)
		self.tree.connect('key-press-event', controller.on_supr_pressed)
		self.delete_all.connect('activate', controller.on_delete_all_clicked)
		self.delete_done_tasks.connect('activate', controller.on_delete_all_done_clicked)
		self.selection.connect("changed", controller.on_tree_selection_changed)
		#self.tree.connect('focus', controller.on_focus_activated)
		#self.tree.connect('focus-out-event', controller.on_focus_out_treeview)


	#metodo con el que mostramos las dos cajas del fondo
	def run_dialog_add(self):
		# self.hbox_add_dialog1.show_all()
		# self.hbox_add_dialog2.show_all()
		self.hbox_add_dialog.show_all()
		
	

	def get_name_buffer_has_text(self):
		return self.name_buffer_has_text

	def get_date_buffer_has_text(self):
		return self.date_buffer_has_text

	#metodo con el que añadimos la tarea a la vista y al modelo
	def run_dialog_add_prueba(self):
		data = (self.tareaEntry.get_text(), self.fechaEntry.get_text(),False)
		# self.tareaEntry.set_text("")
		# self.fechaEntry.set_text("")
		# self.hbox1.hide()
		# self.hbox2.hide()
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

	def get_tasks(self):
		tasklist = []
		#devuelve liststore y treepaths
		selection = self.tree.get_selection().get_selected_rows()
		# print (selection)

		lliststore, treepaths = selection
		for i in range (len(treepaths)):
			treeiter = lliststore.get_iter(treepaths[i])
			# print(i)
			if treeiter != None:
				task = self.store.get(treeiter, 0, 1, 2, 3)
				tasklist.append(task)
				# print(task)
		# print(len(tasklist))
		return tasklist

	def exit(self, parent):
		dialog = Gtk.Dialog(_("¡ATENCIÓN!"), parent, Gtk.DialogFlags.DESTROY_WITH_PARENT, 
				(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
				Gtk.STOCK_OK, Gtk.ResponseType.OK))
		vbox = Gtk.VBox(spacing = 10)
		dialog.get_content_area().add(vbox)
					
		etiqueta1 = Gtk.Label(_("¿Quieres cerrar la aplicación?"))

		etiqueta2 = Gtk.Label(_("Si no se cancela, la aplicación se cerrará"))
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
				
	def update_delete(self, active):
		self._delete_button.set_sensitive(active)

	def update_name_buffer(self, active):
		self.name_buffer_has_text = active
		self.update_add_task(self.get_name_buffer_has_text() 
			& self.get_date_buffer_has_text())

	def update_date_buffer(self, active):
		self.date_buffer_has_text = active
		self.update_add_task(self.get_name_buffer_has_text() 
			& self.get_date_buffer_has_text())

	def update_delete_all_button(self):
		if (len(self.store) == 0):
			self.delete_all.set_sensitive(False)
		else:
			self.delete_all.set_sensitive(True)

	def update_delete_all_done_button(self):
		#miramos si hay alguna tarea marcada como hecha
		for task in self.store:
			if task[3]:
				self.delete_done_tasks.set_sensitive(True)
				return
		#si no hay ninguna, desactivamos el botón
		self.delete_done_tasks.set_sensitive(False)

	def update_menu_options(self):
		self.update_delete_all_button()
		self.update_delete_all_done_button()

	def update_add(self, active):
		self._add_button.set_sensitive(active)

	def update_add_task(self, active):
		self.add_task_button.set_sensitive(active)

	def update_state_on_main_thread(self, state):
		GLib.idle_add(self.update_state, state)

	def update_state(self, state):
		for key, value in state.items():
			method = getattr(self, 'update_state_'+key, None)
			if callable(method):
				method(value, state)

	def update_state_sync_status(self, text, state):
		self._sync_label.set_text(text)

	def update_state_sync_button(self, change, state):
		self._sync_button.set_sensitive(change)

	def update_state_spinner_running(self, start, state):
		if start:
			self.sync_spinner.show()
			self.sync_spinner.start()
		else:
			self.sync_spinner.hide()
			self.sync_spinner.stop()

	def update_state_show_sync_error(self, title, state):
		dialog = Gtk.MessageDialog(self._win, 0, 
			Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
			title)
		dialog.format_secondary_text(_("¡No se puede conectar con el servidor!"))
		dialog.run()
		dialog.destroy()

	def remove_entry_text(self):
		self.tareaEntry.set_text("")
		self.fechaEntry.set_text("")
		# self.hbox_add_dialog1.hide()
		# self.hbox_add_dialog2.hide()
		self.hbox_add_dialog.hide()

	def get_task_list(self):
		# tasklist = []

		# for i in range (len(self.store)):
		# 	treeiter = lliststore.get_iter(treepaths[i])
		# 	# print(i)
		# 	if treeiter != None:
		# 		task = self.store.get(treeiter, 0, 1, 2, 3)
		# 		tasklist.append(task)
		# 		# print(task)
		# # print(len(tasklist))
		# return tasklist
		return self.store

	def remove_selection(self):
		self.tree.get_selection().unselect_all()
		self.update_delete(False)


		
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

	def sync(self):

		def get_random():
			i = randint(1,100)
			return i

		aux = get_random()
		if (aux < 50):
			temp = 80
			success = False
		else:
			temp = 8
			success = True
		for i in range (temp):
			time.sleep(0.2)
		return success

	#metodo que valida el nombre de una tarea, devuelve True si el valor
	#introducido por parametro es valido y False en caso contrario
	def validate_taskname(self, name):
		if (name == ""):
			return False
		return True


	#metodo que valida la fecha de una tarea, devuelve True si el valor
	#introducido por parametro es valido y False en caso contrario
	def validate_taskdate(self, date):
		# if not (datetime.now() < date):
		# 	return False
		# return True
		if not ( (datetime.today().date() <= date.date())):
		  return False
		return True

	#metodo que intenta pasar un string a datetime, en caso de no poder, lanza un 
	#dialogo de error
	def convert_string_to_datetime(self, string_to_convert):
		if (string_to_convert == ""):
			return (None,"void-date")
		else:
			try:
				date = (datetime.strptime(string_to_convert, _DATE_FORMAT))
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
