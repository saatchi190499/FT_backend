# -*- coding: utf-8 -*-
"""
Created on Mon Apr 7th Oct 2019

A singleton class to get the current gap file being used

@author: morans
"""
from lineup_app.GAP_modules import PetexRoutines as PxRoutines
from lineup_app.Config import config
from lineup_app.Models import *
from lineup_app.Model_schemas import *

uploader_dirname = config._uploader_dirname

class GapServer(object):
    class __GapServer:
        def __init__(self):
            self.open_file = None
            self.gap_open = False
            self.pxServer = None
            self.comId = None
            self.locked = False

            server = self.Get_Gap_Server()

            # use the first of the currently selected gap files
            #gap_file = GAPFile.query.filter_by(current=True).first()
            #if gap_file is not None:
            #    self.Open_File(gap_file.location, server)

            #self.Release_Gap_Server(server)
            
            
        def __str__(self):
            return 'self' + self.open_file

        def Get_Gap_Server(self):
            if self.pxServer is None:
                self.pxServer = PxRoutines.Initialize(0)

            if self.gap_open == False :
                self.Run_Gap_Server(self.pxServer)
                
            return self.pxServer

        def Get_Gap_Server_File(self, gapId, session):
            #while self.locked:
            #    raise RuntimeError("The gap server is locked by another part of the program.")
            #print("gap file_locked")
            self.locked = True
            svr = self.Get_Gap_Server()
            gap_file = session.query(GAPFile).filter_by(id=gapId).first()
            #print('GAP File loaded.')
            self.open_file = PxRoutines.DoGet(self.pxServer, "GAP.MOD[{PROD}].FILENAME")
            # don't reopen if the right file is already open
            if (self.open_file == gap_file.location):
                return svr
            self.Open_File(gap_file.location, svr)
            return svr

        def Is_Locked(self):
            return self.locked

        def Release_Gap_Server(self):
            self.locked = False
            #if self.pxServer is not None:
            #    PxRoutines.Stop(self.pxServer)
            #    self.pxServer = None
        
        def Open_File(self, location, pxServer):
            try:
                # reopen the file as the wrong file may be open
                GAPcmd = 'GAP.OPENFILE("' + location + '")'
                PxRoutines.DoCmd(pxServer, GAPcmd)
                self.open_file = location
                print("Started the GAP server and opening the ", location, " gap file. Com id : ", self.comId )
            except PxRoutines.PetexException as e:
                print("Error opening the GAP file.")
                print("Error: ", e.message)
                self.gap_open = False
                self.Release_Gap_Server()
                raise

        def Save_Open_File(self):
            if (self.pxServer is not None):
                PxRoutines.DoCmd(self.pxServer, 'GAP.SAVEFILE("' + self.open_file + '")')

        # Initialise the gap server and open the configured gap file
        def Run_Gap_Server(self, pxServer):

            try:
                if not PxRoutines.DoCmdBool(pxServer,"GAP.SHOWINTERFACE(1)"):
                    #print("Gap application not open, opening app.")
                    #print("Gap application opened successfully.")
                    PxRoutines.DoCmd(pxServer, 'GAP.START("")')
                    self.open_file = None
                    self.gap_open = True

                return True
            except PxRoutines.PetexException as e:
                print("Error starting the GAP server.")
                print("Error: ", e.message)
                self.gap_open = False
                self.Release_Gap_Server()
                return False

    instance = None
    def __new__(cls): # __new__ always a classmethod
        if not GapServer.instance:
            GapServer.instance = GapServer.__GapServer()
        return GapServer.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    


