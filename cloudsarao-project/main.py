#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Importamos el servicio de usuarios para que la aplicacion se integre con las
#   cuentas de usuario de Google.
from google.appengine.api import users
import datetime
# Importamos el archivo persistence.py, que contiene las clases para la persistencia
from persistence import *
from formulario import *

# Importamos el marco de trabajo de aplicaciones web.
import webapp2
import cgi
import jinja2
import os
import logging # Para DEBUG

IMAGEN = '<img class="centrado" src="/img/header.jpg" alt="header">'
CSS = """<head><link rel="stylesheet" type="text/css" href="css/style.css">""" + IMAGEN + """</head>"""


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

#==============================================================================
#==============================================================================
# # Controlador de solicitudes 'MainPage'.
#==============================================================================
#==============================================================================
# RequestHandler se encarga de procesar las peticiones y contruir respuestas.
class MainPage(Handler):
    def get(self):
        s = Sarao.getSaraos()
        self.render('pagina_principal.html', saraos=s)

    def post(self):
        pass

#==============================================================================
#==============================================================================
# # Controlador de solicitudes 'Main Administracion'.
#==============================================================================
#==============================================================================

class Administracion(Handler):
  def get(self):
    s = Sarao.getSaraos()
    self.render('pagina_administracion.html', saraos=s)

#==============================================================================
#==============================================================================
# # Controlador de solicitudes 'Saraos'.
#==============================================================================
#==============================================================================
class NuevoSarao(Handler):
    def post(self):
        key_lugar = cgi.escape(self.request.get('lugar'))
        ma = int(cgi.escape(self.request.get('max_asistentes')))
        h = str(cgi.escape(self.request.get('hora')))
        m = str(cgi.escape(self.request.get('minutos')))

        # Obtenemos los parámetros enviados por POST
        Sarao(nombre = cgi.escape(self.request.get('nombre')),
              fecha = (datetime.datetime.strptime(cgi.escape(self.request.get('fecha')), '%m/%d/%Y')).date(), #Casting a datetime format
              hora = datetime.datetime.strptime(h+":"+m, "%H:%M")
              max_asistentes = ma,
              url = cgi.escape(self.request.get('url')),
              nota = cgi.escape(self.request.get('nota')),
              descripcion = cgi.escape(self.request.get('descripcion')),
              organizacion = cgi.escape(self.request.get('organizacion')),
              lugar = Lugar.getLugar(key_lugar),
              num_asistentes = 0,
              plazas_disponibles = ma
        ).put()
        self.response.write("Añadido sarao.")

    def get(self):
        l = Lugar.getLugares()
        self.render("insertar_sarao.html", lugares=l)

    def realizaAlgunaOperacionGuay(self, numero):
        return numero*numero/2



class NuevoLugar(Handler):
    def post(self):
        Lugar(nombre = cgi.escape(self.request.get('nombre')),
              calle = cgi.escape(self.request.get('calle')),
              cod_postal = int(cgi.escape(self.request.get('cod_postal')))
        ).put()
        self.response.write("Añadido lugar.")

    def get(self):
        self.render("insertar_lugar.html")


class NuevoAsistente(Handler):
  def post(self):
      key_sarao = cgi.escape(self.request.get('id_sarao'))
      a = Asistente(
          correo = cgi.escape(self.request.get('correo')),
          nombre = cgi.escape(self.request.get('nombre')),
          nick_twitter = cgi.escape(self.request.get('nick_twitter')),
          colectivo = cgi.escape(self.request.get('colectivo')),
          procedencia = cgi.escape(self.request.get('procedencia'))
      )
      asis = Asistente.getAsistente(a.correo)
      # No existe
      if asis==None:
          a.asistencia_saraos.append(db.Key(key_sarao))
          a.put()
      # Ya existía
      else:
          asis.asistencia_saraos.append(db.Key(key_sarao))
          asis.put()
      sarao = Sarao.getSarao(key_sarao)
      sarao.num_asistentes += 1
      sarao.plazas_disponibles -= 1
      sarao.put()
      self.response.write("Añadido asistente.")

  def get(self):
      key_sarao = self.request.get('s')
      self.render("insertar_asistente.html",sarao=Sarao.getSarao(key_sarao))


class ModificarSarao(Handler):
  def post(self):
      key_lugar = cgi.escape(self.request.get('lugar'))
      cgi.escape(self.request.get('hora'))
      # Obtenemos los parámetros enviados por POST
      # Sarao(nombre = cgi.escape(self.request.get('nombre')),
      #       fecha = (datetime.datetime.strptime(cgi.escape(self.request.get('fecha')), '%m/%d/%Y')).date(), #Casting a datetime format
      #       #hora = horas+":"+minutos,
      #       max_asistentes = int(cgi.escape(self.request.get('max_asistentes'))),
      #       url = cgi.escape(self.request.get('url')),
      #       nota = cgi.escape(self.request.get('nota')),
      #       descripcion = cgi.escape(self.request.get('descripcion')),
      #       organizacion = cgi.escape(self.request.get('organizacion')),
      #       lugar = Lugar.getLugar(key_lugar)
      # )
  def get(self):
    l = Lugar.getLugares()
    self.render("modificar_sarao.html")


#==============================================================================
#==============================================================================
# # Programa principal.
#==============================================================================
#==============================================================================
# WSGIApplication se encarga de instanciar las ruas de las solicitudes
#   entrantes a los manipuladores basados en la URL.
# Asignamos el controlador de solicitudes (MainPage) a la URL raiz (/), de modo
#   que cuando 'webapp2' recibe una solicitud 'GET HTTP' a la URL '/' se crea
# La informacion acerca de la solicitud se puede obtener usando 'self.request'.
# Asignamos el controlador de solicitudes (Saraos) a la URL '/saraos'.
# debug=True sirve para imprimir la traza de la pila en la salida del
#   navegador.
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/nuevosarao', NuevoSarao),
    ('/nuevolugar', NuevoLugar),
    ('/modificarsarao', ModificarSarao),
    ('/nuevoasistente', NuevoAsistente),
    ('/administracion', Administracion),
], debug=True)
