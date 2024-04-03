# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 14:34:45 2016

@author: zhumbo
"""


import numpy as np
import PetexRoutines as PE



def list2gapstr(l):
    l=list(map(str, l))
    return "|".join(l)+"|"


def filtermasked(par_orig, status, st):
    fpar = []
    for idx, s in enumerate(status):
        if s=="0":
            if st=="bool":
                fpar.append((par_orig[idx]=="1"))
            else:
                fpar.append(par_orig[idx])
                
    if st=="float":
        return np.array(fpar,dtype=float)
    
    else:
        return fpar

# update the original array based on the status mask
def updatepar(par_orig,par,status):
    cnt=0
    for idx,s in enumerate(status):
        if s=="0":
            par_orig[idx]=par[cnt]
            cnt+=1
    return par_orig


def get_all(PE_server,s):
    return PE.DoGet(PE_server,s).split("|")[:-1]

def get_all_float(PE_server,s):
    return np.float_(PE.DoGet(PE_server,s).split("|")[:-1])

def get_all_int(PE_server,s):
    return np.int_(PE.DoGet(PE_server,s).split("|")[:-1])

def get_all_bool(PE_server, s):
    return np.bool_(PE.DoGet(PE_server, s).split("|")[:-1])

def get_float(PE_server,s):
    return float(PE.DoGet(PE_server,s))

def close_pipes(PE_server, pipe_close):
    for p in pipe_close:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].PIPE[{"+p+"}].MASK()")
    return None

def open_pipes(PE_server,pipe_open):
    for p in pipe_open:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].PIPE[{"+p+"}].UNMASK()")
    return None

def open_pipes_id(PE_server,pipe_open):
    for p in pipe_open:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].PIPE["+p+"].UNMASK()")
    return None

def set_pipes(PE_server,pipe_close,pipe_open):
    for p in pipe_close:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].PIPE[{"+p+"}].MASK()")
    for p in pipe_open:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].PIPE[{"+p+"}].UNMASK()")
    return None

def set_well_mask(PE_server, well, mask):
    if mask:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].WELL[{"+well+"}].MASK()")
    else:
        PE.DoCmd(PE_server,"GAP.MOD[{PROD}].WELL[{"+well+"}].UNMASK()")

def choose_unit(PE_server,unit):
    PE.DoCmd(PE_server,"GAP.MOD[{PROD}].SEP[$].MASK()")
    PE.DoCmd(PE_server,"GAP.MOD[{PROD}].SEP[{"+unit+"}].UNMASK()")
    return None

def choose_unit_mask(PE_server, unit):
    PE.DoCmd(PE_server,"GAP.MOD[{PROD}].SEP[$].UNMASK()")
    PE.DoCmd(PE_server,"GAP.MOD[{PROD}].SEP[{"+unit+"}].MASK()")
    return None


def unmask_all_units(PE_server):
    PE.DoCmd(PE_server,"GAP.MOD[{PROD}].SEP[$].UNMASK()")
    return None


def solve_network(PE_server):
    PE.DoCmd(PE_server,"GAP.SOLVENETWORK(0, MOD[0])")
    return None

def solve_network_rb(PE_server):
    PE.DoCmd(PE_server,"GAP.SOLVENETWORK(3, MOD[0])")
    return None

def showinterface(PE_server,s):
    PE.DoCmd(PE_server,"GAP.SHOWINTERFACE("+str(s)+")")
    return None


def get_unit_qgas(PE_server,unit):
    return float(PE.DoGet(PE_server,"GAP.MOD[{PROD}].SEP[{"+unit+"}].SolverResults[0].GasRate"))

def get_unit_qoil(PE_server,unit):
    return float(PE.DoGet(PE_server,"GAP.MOD[{PROD}].SEP[{"+unit+"}].SolverResults[0].OilRate"))

def get_unit_qwat(PE_server,unit):
    return float(PE.DoGet(PE_server,"GAP.MOD[{PROD}].SEP[{"+unit+"}].SolverResults[0].WatRate"))

def set_unit_pres(PE_server,unit,pres):
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].SEP[{"+unit+"}].SolverPres[0]",pres)
    return None


def shut_well(PE_server,well):
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].WELL[{"+well+"}].DPControl","FIXEDVALUE")
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].WELL[{"+well+"}].DPControlValue",10000)
    return None

def open_well(PE_server,well):
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].WELL[{"+well+"}].DPControl","CALCULATED")
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].WELL[{"+well+"}].DPControlValue",0)
    return None

def set_chokes_calculated(PE_server):
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].WELL[$].DPControl","CALCULATED")
    PE.DoSet(PE_server,"GAP.MOD[{PROD}].WELL[$].DPControlValue",0)
    return None

def get_filtermasked(PE_server,s,status,t):
    par_orig=get_all(PE_server,s)
    par=filtermasked(par_orig,status,t)
    return par



def resolve_start(PE_server):
    PE.DoCmd(PE_server, "Resolve.Start()")
    return None

def resolve_openfile(PE_server, s):
    PE.DoCmd(PE_server,'RESOLVE.OPENFILE(\'' + s + '\')')
    return None

def resolve_runscenario(PE_server, sc_name):
    PE.DoCmd(PE_server, 'Resolve.RUNSCENARIO(\'' + sc_name + '\')')
    return None