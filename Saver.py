import os
from os.path import exists
from datetime import datetime
import PySimpleGUI as sg
from glob import glob
from constants import GasesFactors

class Saver:

    def __init__(self, connectedMFC):

        self.folder = os.getcwd() + "/" + datetime.now().strftime("%Y%m%d")
        self.connectedMFC = connectedMFC
        self.openFiles = {}

        self.layout = [
                sg.Button("Registra", key="saver:record"),
                sg.Button("Apri cartella", key="saver:viewFolder"),
                sg.Text("", key="saver:status")
        ]

        self.saving = False


    def parse_events(self, event, values, window):

        if event == "saver:record":
            if self.saving:
                self.endSaving(window)
            else:
                self.beginSaving(window)

        if event == "saver:viewFolder":
            os.startfile( self.folder )
    
    def beginSaving(self, window):
        
        os.makedirs( self.folder, exist_ok=True )

        progr = 0
        while( len( glob( self.folder + f"/MFC{progr:04d}.*.csv" )) > 0 ):
            progr += 1
        
        self.filename = self.folder + f"/MFC{progr:04d}"

        self.saving = True        

        window["saver:status"].update(f"Salvataggio in {self.filename}")
        window["saver:record"].update("Stop")

    def endSaving(self, window):

        self.saving = False
        keys = list( self.openFiles.keys() )
        for k in keys:
            v = self.openFiles.pop( k )
            v.close()

        window["saver:status"].update("")
        window["saver:record"].update("Registra")

    def save_callback(self, MFC, time, value):
        if not self.saving:
            return
        
        if( MFC.port not in self.openFiles ):
            self.openFiles[MFC.port] = open( f"{self.filename}.{MFC.port}.csv", "w", buffering = 1 )
            self.openFiles[MFC.port].write( f"# {MFC.tag} - {MFC.port} - {MFC.serial} - {MFC.gas} ( {GasesFactors[MFC.gas] } )\nTime [millis],Value [{MFC.unit}]\n" )

        self.openFiles[MFC.port].write( f"{time*1000:.0f},{value:.2f}\n" )