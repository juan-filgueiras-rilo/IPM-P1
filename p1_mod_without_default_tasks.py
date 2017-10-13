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
	def on_show_add_dialog_button_clicked(self, widget):
		self._view.update_add(False)
		self._view.run_dialog_add()

	#método que borra una tarea de la vista y el modelo
	def remove_task(self, task):
		if (task != None):
			ok = self._model.remove(task[0])
			if (ok != -1):
				self._view.remove(task[0])
				self._view.remove_selection()
		#actualizamos los botones borrar todas y borras todas las hechas
		self._view.update_menu_options()

	#método que se lanza al seleccionar el botón eliminar, se obtienen las
	#tareas que han sido seleccionadas y las vamos borrando de una en una
	def on_button_remove_clicked(self, widget):
		tasklist = self._view.get_tasks()
		for task in tasklist:
			self.remove_task(task)

	#método que se lanza al intentar cerrar el programa
	def on_button_exit_clicked(self, widget, event):
		signal = self._view.exit(widget.get_toplevel())
		return signal

	#metodo que se lanza al editar la columna fecha de una tarea
	def on_task_date_edit(self, widget, position, text):
		#pasamos el string a datetime
		date = self._model.convert_string_to_datetime(text)
		#comprobamos que es correcta
		if (date == (None,"void-date")):
			self._view.run_dialog_provided_data_error(_("Error"),
					_("La fecha está vacía"))
		elif (date == (None,"bad-format")):
			self._view.run_dialog_provided_data_error(_("Error"),
					_("La fecha introducida no está en el formato correcto (dd/mm/yy)"))
		elif (date == (None,"prior-date")):
			self._view.run_dialog_provided_data_error(_("Error"),
					_("La fecha introducida tiene que ser posterior a la fecha actual"))
		else:
			#obtenemos la tarea que ha sido seleccionada
			tasklist = self._view.get_tasks()
			if ((len(tasklist)) != 0):
				task = tasklist[0]      
				if (task != None):
					task = list(task)
					task[2] = date[0]
					task = tuple(task)
					data = (task[1], task[2], task[3])
					#editamos la fecha en la vista y en el modelo
					ok = self._model.edit(task[0], data)
					if ok != -1:
						self._view.edit(task[0], data)

	#metodo que se lanza al editar la columna nombre de una tarea
	def on_task_name_edit(self, widget, position, text):
		#obtenemos la tarea que ha sido seleccionada
		tasklist = self._view.get_tasks()
		#vemos que hay alguna tarea seleccionada, para evitar errores
		if ((len(tasklist)) != 0):
			#comprobamos que el nombre sea válido
			if not (self._model.validate_taskname(text)):
				self._view.run_dialog_provided_data_error(_("Error"),
					_("El nombre de la tarea no puede estar vacío"))
			else:
				task = self._view.get_tasks()[0]
				if (task != None):
					task = list(task)
					task[1] = text
					task = tuple(task)
					data = (task[1], task[2], task[3])
					#editamos el nombre ne la vista y en el modelo
					ok = self._model.edit(task[0], data)
					if ok != -1:
						self._view.edit(task[0], data)

	#metodo que se lanza al seleccionar la columna hecho        
	def on_row_selected(self, widget, position, n_column):
		if (n_column.get_title() == _("Hecho")):
			task = self._view.get_tasks()[0]
			#convertimos a lista y despues reconvertimos a tupla pq las tuplas son
			#inmutables
			task = list(task)
			#cambiamos su valor
			task[3] = False if task[3] else True
			task = tuple(task)
			data = (task[1], task[2], task[3])
			#editamos en la vista y en el modelo
			ok = self._model.edit(task[0], data)
			if ok != -1:
				self._view.edit(task[0], data)
				self._view.update_menu_options()

	#metodo que se lanza al seleccionar el botón de añadir tarea
	def on_button_add_task_clicked(self, widget):
		#cogemos el texto que ha introducido el usuario
		data = self._view.get_data_from_add_dialog()
		data = list(data)
		#comprobamos que la fecha está bien
		date = self._model.convert_string_to_datetime(data[1])
		if (date == (None,"void-date")):
			self._view.run_dialog_provided_data_error(_("Error"),
					_("La fecha está vacía"))
		elif (date == (None,"bad-format")):
			self._view.run_dialog_provided_data_error(_("Error"),
					_("La fecha introducida no está en el formato correcto (dd/mm/yy)"))
		elif (date == (None,"prior-date")):
			self._view.run_dialog_provided_data_error(_("Error"),
					_("La fecha introducida tiene que ser posterior a la fecha actual"))
		else:
			#actualizamos la fecha de data
			data[1] = date[0]
			#comprobamos que el nombre esté bien
			if not (self._model.validate_taskname(data[0])):
				self._view.run_dialog_provided_data_error(_("Error"),
				_("El nombre de la tarea no puede estar vacío"))
			else:
				data = tuple(data)
				task_id = self._model.add(data)
				if task_id != -1:
					#borramos el texto de los entrys
					self._view.remove_entry_text()
					#activamos el botón que lanza el diálogo de añadir
					self._view.update_add(True)
					#desactivamos el botón para añadir una tarea
					self._view.update_add_task(False)
					#añadimos en la vista y en el modelo
					self._view.add(task_id,data)
					self._view.update_menu_options()

	#método que se lanza al seleccionar el botón sincronizar
	def on_button_sync_clicked(self, widget):
		prev_status = self._view._sync_label.get_text()
		state = {'spinner_running' : True,
				'sync_button' : False,
				'sync_status' : (_("Sincronizando")+'\u2026')}
		self._view.update_state(state)
		t = threading.Thread(target = self.sync, args = (prev_status, ))
		t.start()

	def sync(self, prev_status):
		sync_success = self._model.sync()
		if sync_success:
			state = {'spinner_running' : False,
					'sync_button' : True,
					'sync_status' : _("Última sincronización: ") + time.strftime("%H" + '\u2236' +"%M")}
		else:
			state =  {'spinner_running' : False,
					'sync_button' : True,
					'sync_status' : prev_status,
					'show_sync_error' : _("Error sincronizando")}
		self._view.update_state_on_main_thread(state)

	#método que se lanza al pulsar una tecla en los entrys del diálogo añadir
	def on_key_pressed(self, entry, eventkey):
		#se añade la tarea al pulsar la tecla enter solo si hay buffer en ambos entrys
		if ((eventkey.get_keyval()[1] == 65293) 
				& (self._view.get_name_buffer_has_text()) 
				& (self._view.get_date_buffer_has_text())):
			self.on_button_add_task_clicked(entry)      

	#método que se lanza cada vez que se modifica el campo donde se introduce
	#el nombre de la tarea en el diálogo añadir tarea
	def on_tarea_entry_changed(self, entry):
		length = entry.get_buffer().get_length()
		if (length > 0):
			self._view.update_name_buffer(True)
		else:
			self._view.update_name_buffer(False)

	#método que se lanza cada vez que se modifica el campo donde se introduce
	#la fecha de la tarea en el diálogo añadir tarea
	def on_fecha_entry_changed(self, entry):
		length = entry.get_buffer().get_length()
		if (length > 0):
			self._view.update_date_buffer(True)
		else:
			self._view.update_date_buffer(False)

	#método que se lanza al pulsar una tecla sobre el treeview
	def on_supr_pressed(self, entry, eventkey):
		#comprobamos que la tecla es SUPR
		if ((eventkey.get_keyval()[1] == 65535)):
			self.on_button_remove_clicked(entry)


	#método que se lanza al seleccionar la opción borrar todas las tareas
	def on_delete_all_clicked(self, menuitem):
		#cogemos la lista de tareas y las borramos una a una
		task_list = self._view.get_task_list()
		for task in task_list:
			self.remove_task(task)

	#método que se lanza al seleccionar la opción borrar todas las tareas hechas
	def on_delete_all_done_clicked(self, menuitem):
		#cogemos la lista de tareas
		task_list = self._view.get_task_list()
		#vamos comprobando una a una que tengan el campo hecho activado
		for task in task_list:
			if (task[3]):
				self.remove_task(task)

	def on_tree_selection_changed(self, widget):
		self._view.update_delete(True)

	#método que se lanza al seleccionar el botón de cancelar del diálogo de añadir tarea
	def on_cancel_add_task_button_clicked(self, widget):
		#borramos el texto de los entrys
		self._view.remove_entry_text()
		#activamos el botón que lanza el diálogo de añadir
		self._view.update_add(True)
		#desactivamos el botón para añadir una tarea
		self._view.update_add_task(False)

		
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
			
		#creamos la ventana con el título
		self._win = Gtk.Window()
		self._win.set_size_request(500, 500)
		
		#creamos la header bar donde irán los botones principales
		header_bar = Gtk.HeaderBar()
		header_bar.set_show_close_button(True)
		header_bar.props.title = _("Práctica 1 ") + '\u2013' + _(" IPM 17/18")
		self._win.set_titlebar(header_bar)

		#creamos la caja (vertical) principal de la ventana, donde se meterán todos los elementos
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		#introducimos la caja en la ventana
		self._win.add(box)

		#creamos la ListStore y le añadimos todos los elementos
		self.store = Gtk.ListStore(int, str, GObject.TYPE_PYOBJECT, bool)

		#se crea un treeview sobre la lista store
		self.tree = Gtk.TreeView(self.store)
		#activamos que la activación de una fila se produzca en un simple click en vez 
		#de doble click
		self.tree.set_activate_on_single_click(True)
		self.selection = self.tree.get_selection()
		#desactivamos la búsqueda
		self.tree.set_enable_search(False)
		#activamos la seleccion multiple
		self.selection.set_mode(Gtk.SelectionMode.MULTIPLE) 
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
		column.set_sort_column_id(3)

		#creamos todos los botones que irán en la header bar
		self.show_add_dialog_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_ADD,1)
		self.show_add_dialog_button.get_style_context().add_class('suggested-action')
		self._delete_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_DELETE,1)
		self._delete_button.get_style_context().add_class('destructive-action')
		self._delete_button.set_sensitive(False)
		self._sync_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_REFRESH,1)
		self._sync_button.set_alignment(1,0)
		menu_button = Gtk.MenuButton()

		#creamos el menú y lo asociamos el menu_button
		menu = Gtk.Menu()
		self.delete_all = Gtk.MenuItem(_("Borrar todas las tareas"))
		self.delete_all.show()
		self.delete_done_tasks = Gtk.MenuItem(_("Borrar todas las tareas hechas"))
		self.delete_done_tasks.show()
		menu.append(self.delete_all)
		menu.append(self.delete_done_tasks)
		menu_button.set_popup(menu)
		self.delete_all.set_sensitive(False)

		#espacio donde irá el sync label y sync spinner
		box_sync = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
		self.sync_spinner = Gtk.Spinner()
		self._sync_label = Gtk.Label("")
		#lo alineamos casi abajo del todo
		self._sync_label.set_alignment(0.5, 0.8)
		#dejamos un poco de espacio por arriba y por abajo para que no
		#se vea tan pequeño
		self._sync_label.set_size_request(0, 30)
		


		#diálogo añadir

		#metemos los entrys en una caja nueva por el final
		self.tareaEntry = Gtk.Entry()
		self.fechaEntry = Gtk.Entry()
		#creamos los labels y los justificamos a l izquierda
		name_label = Gtk.Label(_("Nombre"))
		name_label.set_xalign(1)
		date_label = Gtk.Label(_("Fecha"))
		date_label.set_xalign(1)
		#creamos el botón de añadir y lo centramos
		self.add_task_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_ADD, 1)
		self.add_task_button.get_style_context().add_class('suggested-action')
		self.cancel_add_task_button = Gtk.Button.new_from_icon_name(Gtk.STOCK_CANCEL, 1)

		self.add_task_button.set_sensitive(False)
		self.add_task_button.set_alignment(0.5, 0.5)

		#creamos las cajas dónde ira el diálogo añadir (1 horizontal y 3 verticales)
		self.hbox_add_dialog = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 0)
		self.vbox_add_dialog1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
		self.vbox_add_dialog2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
		self.vbox_add_dialog3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 8)


		#lo metemos todo en sus respectivas cajas
		#metemos los elementos de añadir en sus cajas verticales
		self.vbox_add_dialog1.pack_start(name_label, True, True, 0)
		self.vbox_add_dialog1.pack_end(date_label, True, True, 0)
		self.vbox_add_dialog2.pack_start(self.tareaEntry, True, True, 0)
		self.vbox_add_dialog2.pack_end(self.fechaEntry, True, True, 0)
		#espacio que irá entre los bordes de la caja y el botón (arriba y abajo)
		self.vbox_add_dialog3.pack_start(self.add_task_button, True, True, 8)
		self.vbox_add_dialog3.pack_start(self.cancel_add_task_button, True, True, 8)
		#metemos esas 3 cajas en la caja horizontal que englobará a las 3 cajas verticales
		#espacio que irá entre los border de la caja y la caja que metemos a izquierda y derecha
		self.hbox_add_dialog.pack_start(self.vbox_add_dialog1, True, True, 18)
		self.hbox_add_dialog.pack_start(self.vbox_add_dialog2, True, True, 0)
		#espacio que irá entre los border de la caja y la caja que metemos a izquierda y derecha
		self.hbox_add_dialog.pack_end(self.vbox_add_dialog3, True, True, 18)
		#metemos la caja horizontal en la caja principal por el final
		#espacio que irá entre los border de la caja y la caja que metemos arriba y abajo
		box.pack_end(self.hbox_add_dialog, False, False, 18)
		#metemos el treeview en la caja principal por el final
		box.pack_end(self.tree, True, True, 0)
		#metemos los elementos de sincronización en su caja
		box_sync.pack_start(self.sync_spinner, False, False, 0)
		box_sync.pack_start(self._sync_label, True, True, 0)
		#metemos en la header bar los botones que contendrá
		# header_bar.pack_start(menu_button)
		# header_bar.pack_end(self.show_add_dialog_button)
		# header_bar.pack_end(self._delete_button)
		# header_bar.pack_end(self._sync_button)
		header_bar.pack_start(self.show_add_dialog_button)
		header_bar.pack_end(menu_button)
		header_bar.pack_end(self._sync_button)
		header_bar.pack_end(self._delete_button)

		#metemos la caja con los elementos de sincronización en la caja principal por el ppio
		box.pack_start(box_sync, False, False, 0)

		#mostramos todos los elementos menos el diálogo de añadir
		self._win.show_all()
		self.hbox_add_dialog.hide()

		#variables que controlarán si hay texto en los buffers del diálogo añadir
		#por defecto inicializadas a false
		self.name_buffer_has_text = False
		self.date_buffer_has_text = False

		#actualizo los botones del menú contextual, cuento las tareas que hay creadas y/o activadas
		#y se desactivarán en función de si el número de tareas es igual a 0
		self.update_menu_options()

	#todas las señales
	def connect(self, controller):
		self._win.connect("delete-event", controller.on_button_exit_clicked)
		self.show_add_dialog_button.connect('clicked', controller.on_show_add_dialog_button_clicked)
		self._delete_button.connect('clicked', controller.on_button_remove_clicked)
		#seleccionar una fila
		self.tree.connect('row-activated', controller.on_row_selected)
		#editar el nombre de la tarea
		self.renderer_name.connect('edited', controller.on_task_name_edit)
		#editar la fecha de la tarea
		self.renderer_date.connect('edited', controller.on_task_date_edit)
		self.add_task_button.connect('clicked', controller.on_button_add_task_clicked)
		self._sync_button.connect('clicked', controller.on_button_sync_clicked)
		#pulsar Enter en entrys del diálogo de añadir
		self.tareaEntry.connect('key-press-event', controller.on_key_pressed)
		self.fechaEntry.connect('key-press-event', controller.on_key_pressed)
		#buffer alterado
		self.tareaEntry.connect('changed', controller.on_tarea_entry_changed)
		self.fechaEntry.connect('changed', controller.on_fecha_entry_changed)
		#pulsar suprimir sobre el treeview
		self.tree.connect('key-press-event', controller.on_supr_pressed)
		self.delete_all.connect('activate', controller.on_delete_all_clicked)
		self.delete_done_tasks.connect('activate', controller.on_delete_all_done_clicked)
		self.selection.connect("changed", controller.on_tree_selection_changed)
		self.cancel_add_task_button.connect('clicked', controller.on_cancel_add_task_button_clicked)


	#metodo con el que mostramos las dos cajas del fondo
	def run_dialog_add(self):
		self.hbox_add_dialog.show_all()
		
	

	def get_name_buffer_has_text(self):
		return self.name_buffer_has_text

	def get_date_buffer_has_text(self):
		return self.date_buffer_has_text

	#metodo con el que añadimos la tarea a la vista y al modelo
	def get_data_from_add_dialog(self):
		data = (self.tareaEntry.get_text(), self.fechaEntry.get_text(),False)
		return data
		
	#método que muestra un error al introducir mal los datos
	def run_dialog_provided_data_error(self, title, secondary_text):
		dialog = Gtk.MessageDialog(self._win, 0, 
			Gtk.MessageType.INFO, Gtk.ButtonsType.OK, 
			title)
		dialog.format_secondary_text(secondary_text)
		dialog.run()
		dialog.destroy()

	#se devuelve la tarea seleccionada
	def get_task(self):
		task = None
		selection = self.selection
		treeiter = selection.get_selected()[1]
		if treeiter != None:
			task = self.store.get(treeiter,0,1,2,3)
		return task

	#se devuelven todas las tareas seleccionadas
	def get_tasks(self):
		tasklist = []
		#devuelve liststore y treepaths
		selection = self.selection.get_selected_rows()

		lliststore, treepaths = selection
		for i in range (len(treepaths)):
			treeiter = lliststore.get_iter(treepaths[i])
			if treeiter != None:
				task = self.store.get(treeiter, 0, 1, 2, 3)
				tasklist.append(task)
		return tasklist

	#se saca un diálogo y en función de la opción escogida se cerrará el programa o no
	def exit(self, parent):
		dialog = Gtk.Dialog(_("¡Atención!"), parent, Gtk.DialogFlags.DESTROY_WITH_PARENT, 
				(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
				Gtk.STOCK_OK, Gtk.ResponseType.OK))
		vbox = Gtk.VBox(spacing = 10)
		#meto el diálogo en la caja
		dialog.get_content_area().add(vbox) 
		#creo los etiquetas con el texto
		etiqueta1 = Gtk.Label(_("¿Quieres cerrar la aplicación?"))
		etiqueta2 = Gtk.Label(_("Si no se cancela, la aplicación se cerrará"))
		#meto ambas por el principio del diálogo
		vbox.pack_start(etiqueta1, True, True, 0)
		vbox.pack_start(etiqueta2, True, True, 0)
		vbox.show_all()
		#cojo la respuesta del usuario
		respuesta = dialog.run()
		#en función de la respuesta, cierro el programa o no
		if respuesta == Gtk.ResponseType.OK:
			Gtk.main_quit()
		else:
			dialog.destroy()
			return True

	#método añadir tareas a la liststore
	def add(self, task_id, data):
		data = list(data)
		data.insert(0,task_id)
		data = tuple(data)
		self.store.append(data)

	#método editar una tarea de la liststore
	def edit(self, task_id, data):
		for task in self.store:
			if task[0] == task_id:
				self.store.set(task.iter, 1, data[0], 2, data[1], 3, data[2])

	#método borrar una tarea de la liststore (por task_id)
	def remove(self, task_id):
		for task in self.store:
			if task[0] == task_id:
				self.store.remove(task.iter)
	
	#método para actualizar el botón de borrar      
	def update_delete(self, active):
		self._delete_button.set_sensitive(active)

	#método que actualiza la variable que controlan el buffer nombre del diálogo añadir
	#y además actualiza el botón añadir tarea
	def update_name_buffer(self, active):
		self.name_buffer_has_text = active
		self.update_add_task(self.get_name_buffer_has_text() 
			& self.get_date_buffer_has_text())

	#método que actualiza la variable que controlan el buffer fecha del diálogo añadir
	#y además actualiza el botón añadir tarea
	def update_date_buffer(self, active):
		self.date_buffer_has_text = active
		self.update_add_task(self.get_name_buffer_has_text() 
			& self.get_date_buffer_has_text())

	#método que actualiza el botón borrar todas las tareas del menú contextual
	def update_delete_all_button(self):
		if (len(self.store) == 0):
			self.delete_all.set_sensitive(False)
		else:
			self.delete_all.set_sensitive(True)

	#método que actualiza el botón borrar todas las tareas hechas del menú contextual
	def update_delete_all_done_button(self):
		#miramos si hay alguna tarea marcada como hecha
		for task in self.store:
			if task[3]:
				self.delete_done_tasks.set_sensitive(True)
				return
		#si no hay ninguna, desactivamos el botón
		self.delete_done_tasks.set_sensitive(False)

	#método que llama a los dos métodos anteriores
	def update_menu_options(self):
		self.update_delete_all_button()
		self.update_delete_all_done_button()

	#método que actualiza el bóton que lanza el diálogo añadir
	def update_add(self, active):
		self.show_add_dialog_button.set_sensitive(active)

	#método que actualiza el botón de añadir una tarea
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

	#método que limpia los entrys del diálogo añadir y además los oculta
	def remove_entry_text(self):
		self.tareaEntry.set_text("")
		self.fechaEntry.set_text("")
		self.hbox_add_dialog.hide()

	#método que devuelve la liststore
	def get_task_list(self):
		return self.store

	#método que des-selecciona todo
	def remove_selection(self):
		self.selection.unselect_all()
		self.update_delete(False)
		
'''
Modelo
'''

class TaskList_Model:

	def __init__(self):
		self.ID = 0
		self.model_task_list = []

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

	#edita la tarea de la lista y devuelve su id en caso de que la operación se haya
	#podido realizar (-1 en caso contrario)
	def edit(self, task_id, data):
		done = -1
		#cojo el ID para buscar si está ese elemento en la lista
		for task in self.model_task_list:
			if task_id == task[0]:
				task = (task_id, data[0], data[1], data[2])
				done = task_id
				break
		return done

	#borra la tarea de la lista y devuelve su id en caso de que la operación se haya
	#podido realizar (-1 en caso contrario)
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
