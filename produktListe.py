#!/usr/bin/python3

"""
Main executable for the produktListe
"""

import src.produktListe.listframe
import src.produktListe.produktapp


if __name__ == "__main__":

    pl = src.produktListe.produktapp.ProduktApp()
    pl.run()
