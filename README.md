<<<<<<< HEAD
Material para la práctica 1 de IPM. Las instrucciones están en el fichero del
enunciado.
=======
TGR 1 - Interfaces Persona Máquina Curso 17/18
=========================================

El primer TGR consistirá en una serie de ejercicios para aprender a utilizar Git y a trabajar con el repositorio de la Facultad.

# 1. Configuración de cuenta en git.fic.udc.es

La Facultad de Informática dispone de su propio servidor git gestionado a través de la aplicación GitLab. Puedes acceder a el a través de la siguiente url:

https://git.fic.udc.es/users/sign_in

Utiliza tus credenciales de los servicios de la UDC para entrar en la aplicación.

Para poder conectar tu ordenador a GitLab es necesario subir tu clave SSH pública a GitLab en la siguiente página:

https://git.fic.udc.es/profile/keys

En esta misma página puedes encontrar información de cómo generar tu clave SSH en varios sistemas operativos.

**Importante**: Tu clave pública está asociada a tu cuenta de usuario de tu ordenador por lo que no te podrás conectar a tu repositorio desde otra cuenta de usuario, desde otro ordenador, desde otro sistema operativo o desde una reinstalación del sistema operativo. Existen dos posibles soluciones a este problema:

* Generar una nueva clave SSH en esa nueva cuenta/ordenador/sistema operativo/reinstalación y subir la nueva clave a https://git.fic.udc.es/profile/keys.
* Hacer una copia de seguridad de tus claves SSH y copiar dichas claves a la nueva cuenta/ordenador/sistema operativo/reinstalación.


# 2. Dependencias

Para realizar este TGR necesitarás instalar en tu ordenador:

* git
* python 3.X
* gtk 3
* pip3

Para ejecutar los tests es necesario instalar la librería *aloe*

```
	$ pip3 install aloe
```

# 3. Ejercicios

## 3.1. Creación de un repositorio local

1. Crea el directorio `ipm-tgr1`
2. Descarga en el directorio  `ipm-tgr1` el código fuente de https://git.fic.udc.es/noelia.barreira/ipm-tgr1/
3. Crea un repositorio local en el directorio `ipm-tgr1`
4. Crea un fichero `nombres.txt` en el directorio  `ipm-tgr1` cuyo contenido tenga el siguiente formato: `Apellidos alumno, Nombre alumno`
5. Añade ese fichero al repositorio git local
6. Haz un commit

## 3.2 Creación de un repositorio remoto

Crea un nuevo repositorio privado denominado `ipm-tgr1` en https://git.fic.udc.es/projects/new  y asocialo al repositorio local.

Tras crear tu reposorio remoto, GitLab te proporcionará información sobre los pasos a seguir para asociar tu repositorio remoto con tu repositorio local (ver secciones *Git global setup* y *Existing Git repository*).

## 3.3 Sincronización de repositorios

En el directorio `ipm-tgr1`:

1. Sube los cambios del repositorio local al repositorio remoto.
2. Comprueba si has realizado correctamente estos pasos con aloe:

```
    $ aloe -x --verbosity=3 features/test1.feature
```

Si todo está correcto, los tests definidos en el fichero `test1.feature` se ejecutarán sin problemas. Si algún test falla, corrige el problema.

Nota: En las pruebas de *aloe*, el repositorio remoto se descarga por defecto en el directorio `/tmp`. Si este directorio no existe en tu sistema operativo, edita el fichero `features/steps.py` y especifica un directorio válido en la línea 10 de dicho fichero:

```
DIR_TMP = '/tmp'
```


## 3.4 Creación de etiquetas

En el directorio `ipm-tgr1`:

1. Crea la etiqueta `task1` en el repositorio local
2. Sube los cambios del repositorio local al repositorio remoto. *Hint*: Debes usar la opción `--tags`
3. Comprueba si has realizado correctamente estos pasos con aloe:

```
    $ aloe -x --verbosity=3 features/test2.feature
```

Si todo está correcto, los tests definidos en el fichero `test2.feature` se ejecutarán sin problemas. Si algún test falla, corrige el problema.

## 3.5 HolaMundo en python

En el directorio `ipm-tgr1`:

1. Crea el fichero `holamundo.py` que abra una ventana Gtk en python con el titulo *Hola mundo*.
2. Añade permisos de ejecución al fichero `holamundo.py`

```
$ chmod u+x holamundo.py
```

3. Añade ese fichero al repositorio git local
4. Haz un nuevo commit
5. Comprueba si has realizado correctamente estos pasos con aloe:

```
    $ aloe -x --verbosity=3 features/test3.feature
```

Si todo está correcto, los tests definidos en el fichero `test3.feature` se ejecutarán sin problemas. Si algún test falla, corrige el problema.



## 3.6 Sincronización de repositorios

1. Asigna la etiqueta `task2` al último commit
2. Sube los nuevos cambios al repositorio remoto. No te olvides de subir las etiquetas!
3. Comprueba si has realizado correctamente estos pasos con aloe:

```
    $ aloe -x --verbosity=3 features/test4.feature
```

Si todo está correcto, los tests definidos en el fichero `test4.feature` se ejecutarán sin problemas. Si algún test falla, corrige el problema.
>>>>>>> d6a523d140cf3c515d6940b6f87dd5f022a0140c
