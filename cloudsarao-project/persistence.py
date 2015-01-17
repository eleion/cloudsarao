#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

#==============================================================================
#==============================================================================
# # Clase Lugar
#==============================================================================
#==============================================================================
class Lugar(db.Model):
    nombre = db.StringProperty(required=True)
    calle = db.StringProperty(required=True)
    cod_postal = db.IntegerProperty()

    @classmethod
    def getLugares(self):
        return self.all()

    @classmethod
    def getLugar(self, key):
        return Lugar.gql("WHERE __key__ = :n", n=db.Key(key)).get()


#==============================================================================
#==============================================================================
# # Clase Sarao
#==============================================================================
#==============================================================================
# Esta clase tiene los siguientes atributos:
# - nombre : Nombre del Sarao.
# - fecha : Fecha de realizacion del Sarao.
# - max_asistentes : El numero máximo de asistentes que puede asistir al
#                   Sarao.
# - num_asistentes : Número de asistentes que están apuntados al Sarao.
# - url : Dirección web del Sarao.
# - nota : Todo tipo de notas aclaratorias asociadas al Sarao.
# - descripcion : Descripción del evento.
class Sarao(db.Model):
  # Atributos del sarao.
    nombre         = db.StringProperty(required=True)
    fecha          = db.DateProperty(required=True)
    hora           = db.DateProperty()
    max_asistentes = db.IntegerProperty(required=True)
    url            = db.StringProperty()
    nota           = db.StringProperty()
    descripcion    = db.TextProperty()
    organizacion   = db.StringProperty()
    limite_inscripcion = db.DateProperty()
    plazas_disponibles = db.IntegerProperty()
    # Relación uno-a-muchos
    lugar          = db.ReferenceProperty(Lugar, collection_name='lugares')

    @property
    def asistentes(self):
        return Asistente.gql("WHERE asistencia_saraos = :1", self.key()).run()

    @classmethod
    def getSaraos(self):
        return self.all()

    @classmethod
    def getSarao(self, key):
        return Sarao.gql("WHERE __key__ = :n", n=db.Key(key)).get()



#==============================================================================
#==============================================================================
# # Clase Asistente
#==============================================================================
#==============================================================================
class Asistente(db.Model):
    correo = db.EmailProperty(required=True)
    nombre = db.StringProperty(required=True)
    nick_twitter = db.StringProperty()
    colectivo = db.StringProperty(required=True, choices=('alumno', 'PDI', 'PAS', 'otro'))
    procedencia = db.StringProperty()
    #Relacion muchos-muchos de saraos y asistentes
    asistencia_saraos = db.ListProperty(db.Key)
