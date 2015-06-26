__author__ = 'Danylo Bilyk'

from .census import Census


class Catalogue(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(Catalogue, cls).__new__(cls, clsname, bases, attrs)
        protocol = Census()
        if not protocol.contains(newclass):
            protocol.add(newclass)
        return newclass
