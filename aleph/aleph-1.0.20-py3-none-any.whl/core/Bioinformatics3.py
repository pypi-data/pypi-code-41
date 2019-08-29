#! /usr/bin/env python
# -*- coding: utf-8 -*-

#future imports
from __future__ import print_function
from __future__ import division

#from __future__ import unicode_literals

#System imports
import sys
import os
import copy
import shutil
from collections import defaultdict

# Python standard modules imports
import pickle
import operator
import itertools
import traceback

import io
import gzip
import shutil

#Scientific and numerical imports
import Bio.PDB
import numpy
import scipy
import scipy.stats
import csb.bio.utils

#Other imports
from termcolor import colored
import igraph
import igraph.vendor.texttable

#ARCIMBOLDO_FULL imports
import ALEPH

try:
    import urllib
except ImportError:
    import urllib2

import SystemUtility

#AAList = ['ALA', 'ASX', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE', 'LYS', 'LEU', 'MET', 'ASN', 'PRO', 'GLN',
#          'ARG', 'SER', 'THR', 'SEC', 'VAL', 'TRP', 'XAA', 'TYR', 'GLX', 'PYL', 'UNK', 'XLE', 'MSE', 'ME0', 'CGU']

AADICMAP = {'ALA': 'A', 'CYS': 'C', 'CSO': 'C', 'OCS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K',
            'LEU': 'L', 'MET': 'M', 'MSE': 'M', 'SAM': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R', 'SER': 'S', 'THR': 'T', 'KCX': 'K',
            'VAL': 'V', 'TRP': 'W', 'TYR': 'Y', 'UNK': '-', 'SEC': 'U', 'PYL': 'O', 'ASX': 'B', 'GLX': 'Z', 'XLE': 'J', 'FOL': 'X', 'DAL': 'A',
            'XAA': 'X', 'ME0': 'M', 'CGU': '-'}

AADICMAP = defaultdict(lambda: "X", **AADICMAP)

AAList = AADICMAP.keys()
ATOAAAMAP =  dict((v,k) for k,v in AADICMAP.items())
AALISTOL = AADICMAP.values()

list_id = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'  # All possible chain ids for a PDB


def set_occupancy_to_zero_for_outliers(structure,model,dizio_resi):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure: Bio.PDB.Structure
    :param model: int
    :param dizio_resi: dict
    :return: Bio.PDB.Structure
    """
    for resi in get_list_of_residues(structure,model):
        if resi.get_full_id()[1:4] not in [ren[1][1:4] for ren in dizio_resi.values()]:
            for atom in resi:
                atom.set_occupancy(0.0)
    return structure

def trim_ensemble_to_distance(pdb,codec,distance):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param pdb:
    :param codec:
    :param distance:
    :return:
    """
    if (isinstance(pdb,str) and os.path.exists(pdb)) or isinstance(pdb,io.StringIO):
        if isinstance(pdb,io.StringIO):
            pdb.seek(0)
        structure1 = get_structure("a",pdb)
        list_CA1 = [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(structure1,'R') if residue.has_id("CA")]
    else:
        list_CA1 = pdb

    distance_hash = {ca1.get_full_id(): [(ca1-ca2,ca2.get_full_id(),ca1,ca2) for ca2 in list_CA1 if ca1.get_full_id()[1]!=ca2.get_full_id()[1]] for ca1 in list_CA1}
    eliminate = []
    pairs = {}
    for key in distance_hash:
        lista = sorted(distance_hash[key], key=lambda x: (x[0],x[1][1]))
        models = []
        zer = []
        for one in lista:
            if one[1][1] not in models and one[0]<=distance and one[0]>0:
                zer.append(one)
                models.append((one[1][1],one[1]))

        if key[1] not in pairs:
            pairs[key[1]] = {m[0]:[m[1]] for m in models}
        else:
            for tk in models:
                if tk[0] not in pairs[key[1]]:
                    pairs[key[1]][tk[0]] = [tk[1]]
                else:
                    pairs[key[1]][tk[0]].append(tk[1])

        if len(zer) > 0:
            distance_hash[key] = zer
        else:
            eliminate.append(key)

    for key in eliminate:
        del distance_hash[key]

    atoms = set([])
    for cosmo in distance_hash.keys():
        atoms.add((cosmo, distance_hash[cosmo][0][2]))
        for idr in distance_hash[cosmo]:
            atoms.add((idr[1], idr[3]))
    atoms = sorted(list(atoms))
    models = {}
    for atm in atoms:
        if atm[0][1] not in models:
            models[atm[0][1]] = [atm[1]]
        else:
            models[atm[0][1]].append(atm[1])

    size_frag = 2
    for model in models:
        models[model] = sorted(list(set(models[model])),key=lambda x: x.get_full_id())
        remove = []
        #print("This is model",model)
        cont = 0
        frags = set([])
        for e in range(len(models[model])-1):
            frags.add(e)
            if check_continuity(models[model][e].get_parent(), models[model][e+1].get_parent(), verbose=False):
                cont += 1
                frags.add(e+1)
            else:
                if cont < size_frag:
                    for c in frags:
                        #print("Removing..",models[model][c].get_full_id())
                        remove.append(c)
                frags = set([])
                cont = 0

        remove = sorted(remove,reverse=True)
        for rem in remove:
            del models[model][rem]


    #quest = []
    kk_to_del = []
    for key,value in pairs.items():
        #print("----",key,value)
        key_to_del = []
        for v in value.keys():
            value[v] = sum([1 for t in value[v] if t in [s.get_full_id() for s in models[v]]])
            if value[v] == 0:
                key_to_del.append(v)

        for v in key_to_del:
            del value[v]

        #print("++++",key,value)
        pairs[key] = value
        if len(value.keys()) == 0:
            kk_to_del.append(key)

        #TODO: here I can force to check a minimum amount of number of contacts to allow insertion in the quest list
        #quest.append([key]+list(value.keys()))

    for v in kk_to_del:
        del pairs[v]

    all_reductions = []
    for p in sorted(pairs.keys(), key=lambda x: len(pairs[x].keys()), reverse=True):
        queue = [(p,0)]
        for t in sorted(pairs[p].keys(), key=lambda x: pairs[p][x], reverse=True):
            insert = True
            for c in queue:
                if t not in pairs[c[0]]:
                    insert = False
                    break
            if insert:
                queue.append((t, pairs[p][t]))
        print("Reduction:",queue)
        all_reductions.append(queue)

    if len(all_reductions) <= 0:
        return ""

    result = set(sorted(all_reductions, key=lambda x: (len(x), sum([o[1] for o in x])), reverse=True)[0])

    # quest = sorted(quest,key=lambda x: len(x), reverse=True)
    #
    # result = set(quest[0])
    # visited = [quest[0][0]]
    # for s in quest[1:]:
    #     tr = result.copy()
    #     result.intersection_update(s)
    #     visited.append(s[0])
    #     print("Exploring intersection:",result)
    #     if all([pr in visited for pr in result]):
    #         break
    #     if len(result) < 4:
    #         result = tr
    #         print("going back to",result)
    #         break
    print("Final models selected",result)
    result = set([o[0] for o in result])

    #distance_hash2 = {key: sorted(distance_hash[key], key=lambda x: (x[0],x[1][1]))[0] for key in distance_hash if (sorted(distance_hash[key], key=lambda x: (x[0],x[1][1]))[0][0] <= distance)}

    pdball = ""
    for model in sorted(models.keys()):
        if model in result:
            pdball += "MODEL " + str(model) + "\n"
            pdball += "REMARK TITLE " + codec[model] + "\n"
            pdball += get_pdb_from_list_of_atoms(models[model], renumber=False, uniqueChain=False, chainId="A", chainFragment=False, diffchain=None, polyala=False, maintainCys=False, normalize=False, sort_reference=True)[0]
            pdball += "ENDMDL" + "\n"

    return pdball

def distance_between_matrices(alist,blist,are_cosins=False,verbose=False, weights_list=None, stat_test=True):
    #numpy.seterr(all='raise')
    try:
        a = numpy.concatenate([cc.flatten() for cc in alist])
        b = numpy.concatenate([dd.flatten() for dd in blist])

        if weights_list is not None:
            weights = numpy.concatenate([ee.flatten() for ee in weights_list])
        else:
            weights = None
        e = None
        if stat_test and a.shape[0]>20:
        #    #if not t_student(a,b,weights=weights, p_value=0.05): return 0.0 #Not comparable too different
            e = mann_whitney(a,b, are_cosins=are_cosins, weights=None, p_value=0.1, verbose=False)

        sigma = 1
        if a.shape[0]<20:  sigma = 2

        if not are_cosins:
            ddd = a - b
            max_one = a.copy()
            max_one[numpy.where(ddd < 0)] = b[numpy.where(ddd < 0)]
            Z = numpy.abs(ddd) / max_one

            if weights is not None and weights.shape == Z.shape:
                mean = numpy.average(Z,weights=weights)
                std = numpy.sqrt(numpy.average((Z-mean)**2, weights=weights))
            else:
                mean = numpy.mean(Z)
                std = numpy.std(Z)
            diff = 1.0 - (mean+(sigma*std))
            if e is not None :
                if e: diff += 0.1
                elif diff<0.8: diff -= 0.2 #0.15
            #if a.shape[0]<20:  diff -= 0.1
        else:
            #NOTE: The current defaults values are already normalized in (0, 1) from the uniform distributed degree angles

            #NOTE: The following normalization is to trasform cosins (-1, 1) to (0,1). Trouble is that cosin is not uniformely distributed
            # a = (((a+1.0) * 2) / 2.0) / 2.0
            # b = (((b+1.0) * 2) / 2.0) / 2.0
            #NOTE: The following normalization is to transform angles in radians in (0, 1). Tried but It does not work as good as with degrees
            #a /= numpy.pi
            #b /= numpy.pi

            ddd = a - b
            Z = numpy.abs(ddd) #/ max_one #/ 2.0 #/ (numpy.pi) #numpy.pi or 2*numpy.pi???
            if weights is not None and weights.shape == Z.shape:
                mean = numpy.average(Z, weights=weights)
                std = numpy.sqrt(numpy.average((Z - mean) ** 2, weights=weights))
            else:
                mean = numpy.mean(Z)
                std = numpy.std(Z)
            diff = 1.0 - (mean+(sigma*std))
            if e is not None:
                if e: diff += 0.1
                elif diff<0.8: diff -= 0.2 #0.15
            #if a.shape[0]<20:  diff -= 0.1

        #verbose=True
        # if weights is not None:
        #     print(list(Z))
        #     print(list(weights))
        if verbose: #and diff>0.3 and not are_cosins: #and diff>0.10:
            print("A", a)
            print("B", b)
            print("a-b", abs(a - b))
            print("Z",Z)
            #print("maxone", max_one)
            print("ANGLE:" if are_cosins else "DIST:","Mean",numpy.mean(Z),"STD",numpy.std(Z),"MEAN + STD",(numpy.mean(Z)+numpy.std(Z)),
                  "MeanW",mean,"STDW",std,"MEANW + STDW",(mean+std), "diff1",1.0 - (mean+(sigma*std)), "diff2",diff)

    except:
        #print(sys.exc_info())
        #traceback.print_exc(file=sys.stdout)
        print("A", a)
        print("B", b)
        print("a-b", abs(a - b))
        print("maxone", max_one)
        print("Z",Z)
        print("diff",diff)

    return diff

def t_student(a,b,weights=None,p_value=0.05):
    aa = a.copy()
    bb = b.copy()
    if weights is not None:
        aa = (aa*weights).flatten()
        bb = (bb*weights).flatten()
    else:
        aa = aa.flatten()
        bb = bb.flatten()
    t2, p2 = scipy.stats.ttest_ind(aa, bb, equal_var=False)

    # print("t = " + str(t2))
    # print("p = " + str(p2))
    if p2<=p_value:
        #print("Significant: Means are statistically different. So they are not comparable")
        return False
    else:
        return True

def mann_whitney(a,b,weights=None, are_cosins=False, p_value=0.05, verbose=False):
    aa = a.copy()
    bb = b.copy()

    if not are_cosins:
        ddd = aa - bb
        max_one = a.copy()
        max_one[numpy.where(ddd < 0)] = bb[numpy.where(ddd < 0)]
        aa = aa / max_one
        bb = bb / max_one

    if weights is not None:
        aa = (aa*weights).flatten()
        bb = (bb*weights).flatten()
    else:
        aa = aa.flatten()
        bb = bb.flatten()
    try:
        t2, p2 = scipy.stats.mannwhitneyu(aa, bb)
    except ValueError:
        if verbose:
            print("Result is pvalue is more than threhsold")
            print()
            print(list(aa))
            print(list(bb))
            print("t = " + str(t2))
            print("p = " + str(p2))
            print()
        return True

    if p2<=p_value:
        # if verbose:
        #     print("Result is pvalue is less than threhsold")
        #     print()
        #     print(list(aa))
        #     print(list(bb))
        #     print("t = " + str(t2))
        #     print("p = " + str(p2))
        #     print()
        return False
    else:
        if verbose:
            print("Result is pvalue is more than threhsold")
            print()
            print(list(aa))
            print(list(bb))
            print("t = " + str(t2))
            print("p = " + str(p2))
            print()
        return True

def get_CA_distance_dictionary(pdb_model1, pdb_model2, max_rmsd=0.5, last_rmsd=1.0, recompute_rmsd=True, cycles=3, cycle=1, before_apply=None, get_superposed_atoms=False, force_reference_residues=False, data_tuple = None):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param pdb_model1:
    :param pdb_model2:
    :param max_rmsd:
    :param last_rmsd:
    :param recompute_rmsd:
    :param cycles:
    :param cycle:
    :param before_apply:
    :param get_superposed_atoms:
    :param force_reference_residues:
    :param data_tuple:
    :return:
    """
    if (isinstance(pdb_model1,str) and os.path.exists(pdb_model1)) or isinstance(pdb_model1,io.StringIO):
        if isinstance(pdb_model1,io.StringIO):
            pdb_model1.seek(0)
        structure1 = get_structure("a",pdb_model1)
        list_CA1 = [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(structure1,'R') if residue.has_id("CA")]
    else:
        list_CA1 = pdb_model1

    if (isinstance(pdb_model2,str) and os.path.exists(pdb_model2)) or isinstance(pdb_model2,io.StringIO):
        if isinstance(pdb_model2,io.StringIO):
            pdb_model2.seek(0)
        structure2 = get_structure("b",pdb_model2)
        list_CA2 = [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(structure2,'R') if residue.has_id("CA")]
    else:
        list_CA2 = pdb_model2

    if cycle == cycles:
        max_rmsd = last_rmsd
    #print("PDBMODEL1",type(pdb_model1),"PDBMODEL2",type(pdb_model2),"len(1)",len(list_CA1),"len(2)",len(list_CA2),"type(1)",type(list_CA1),"type(2)",type(list_CA2))
    rmsd = 100
    if before_apply is not None and isinstance(before_apply,tuple) or isinstance(before_apply,list):
        R, t = before_apply
        # print("---",full_ca[0].get_full_id(),full_ca[0].get_coord())
        #NOTE: it is essential that R,t corresponds to the transformation of the pdb_model2 onto pdb_mopdel1
        list_CA2 = transform_atoms(list_CA2, R, t)
    elif before_apply is not None and isinstance(before_apply,str) and before_apply == "automatic":
        allatoms_ana = [atm for res in list_CA2 for atm in res.get_parent()]
        list_CA2, rmsd, R, t = get_rmsd_and_RT(list_CA1, list_CA2, allatoms_ana)
        list_CA2 = [atom for atom in allatoms_ana if atom.get_name().lower() == "ca"]
        print("rmsd initial using all atoms is",rmsd)

    distance_hash = {ca1.get_full_id(): [(ca1-ca2,ca2.get_full_id(),ca1,ca2) for ca2 in list_CA2] for ca1 in list_CA1}
    if not force_reference_residues or data_tuple is None:
        distance_hash2 = {key:sorted(distance_hash[key], key=lambda x: x[0])[0] for key in distance_hash if (sorted(distance_hash[key], key=lambda x: x[0])[0][0] <= max_rmsd) or (sorted(distance_hash[key], key=lambda x: x[0])[0][0] <= max_rmsd+1.0 and
                                                                                                                                                                (key[0],key[1],key[2],(key[3][0],key[3][1]-1,key[3][2]),key[4]) in distance_hash and
                                                                                                                                                                              sorted(distance_hash[(key[0],key[1],key[2],(key[3][0],key[3][1]-1,key[3][2]),key[4])], key=lambda x: x[0])[0][0] <= max_rmsd and
                                                                                                                                                                              (key[0],key[1],key[2],(key[3][0],key[3][1]+1,key[3][2]),key[4]) in distance_hash and
                                                                                                                                                                              sorted(distance_hash[(key[0],key[1],key[2],(key[3][0],key[3][1]+1,key[3][2]),key[4])], key=lambda x: x[0])[0][0] <= max_rmsd)}
        todelete = []

        for i, key in enumerate(sorted(distance_hash2.keys())):
            prev = False
            post = False
            if i > 0 and (key[0], key[1], key[2], (key[3][0], key[3][1] - 1, key[3][2]), key[4]) in distance_hash2:
                prev = True
            if i < len(distance_hash2.keys()) - 1 and (
            key[0], key[1], key[2], (key[3][0], key[3][1] + 1, key[3][2]), key[4]) in distance_hash2:
                post = True

            if not (prev or post):
                todelete.append(key)

        for key in todelete:
            del distance_hash2[key]
    else:
        distance_hash2 = {key:sorted(distance_hash[key], key=lambda x: x[0]) for key in distance_hash if (sorted(distance_hash[key], key=lambda x: x[0])[0][0] <= max_rmsd) or (sorted(distance_hash[key], key=lambda x: x[0])[0][0] <= max_rmsd+1.0 and  (key[0],key[1],key[2],(key[3][0],key[3][1]-1,key[3][2]),key[4]) in distance_hash and
                                                                                                                                                                              sorted(distance_hash[(key[0],key[1],key[2],(key[3][0],key[3][1]-1,key[3][2]),key[4])], key=lambda x: x[0])[0][0] <= max_rmsd and
                                                                                                                                                                              (key[0],key[1],key[2],(key[3][0],key[3][1]+1,key[3][2]),key[4]) in distance_hash and
                                                                                                                                                                              sorted(distance_hash[(key[0],key[1],key[2],(key[3][0],key[3][1]+1,key[3][2]),key[4])], key=lambda x: x[0])[0][0] <= max_rmsd)}

        #1: Find the contact points between paired strands:
        (graph_ref, graph_targ, associations_list, map_reference, map_target) = data_tuple

        map_target = {k[2:4]:v for k,v in map_target.items()}
        map_reference = {k[2:4]:v for k,v in map_reference.items()}

        possibi = []
        for associations in associations_list:
            centers_ref = []
            corresp = []
            mins = []
            for fragr in graph_ref.vs:
                fragrl = [tuple(tr[2:4]) for tr in fragr["reslist"]]
                namer = fragr["name"]
                corre = associations[namer]
                lipol = []
                for key in distance_hash2.keys():
                    if key[2:4] in fragrl:
                        for q,value in enumerate(distance_hash2[key]):
                            if map_target[value[1][2:4]] == corre:
                                lipol.append((value,key[2:4]))
                                break
                lipo = sorted(lipol, key=lambda x:x[0][0])[0]
                diffe = [abs(lipol[c+1][0][0]-lipol[c][0][0]) for c in range(len(lipol)-1)]
                #print("DIFFE",diffe)
                where = fragrl.index(lipo[1])
                centers_ref.append(((0,where,len(fragrl)), fragr["reslist"][where]))
                corresp.append((centers_ref[-1],lipo[0]))
                mins.append(lipo[0][0])
            print("ASSO",associations)
            print("MINS",mins)
            possibi.append((sum(mins)/len(mins),associations,centers_ref,corresp))

        (score_possi, associations, centers_ref, corresp) = sorted(possibi, key=lambda x: x[0])[0]
        #centers_ref = [((0,round(int(len(frag["reslist"])/2)),len(frag["reslist"])),frag["reslist"][round(int(len(frag["reslist"])/2))]) for frag in graph_ref.vs]
        map_secstr_ref = {tuple(key[1:4]):frag.index for frag in graph_ref.vs for key in [tuple(k[1:4]) for k in frag["reslist"]]}
        map_secstr_targ = {tuple(key[1:4]):frag.index for frag in graph_targ.vs for key in [tuple(k[1:4]) for k in frag["reslist"]]}
        #corresp = [(center,distance_hash2[tr][0]) for center in centers_ref for tr in distance_hash2.keys() if tuple(tr[2:4])==tuple(center[1][2:4])]

        #print("CENTERS_REF",centers_ref)
        #print("MAP SECSTR REF",map_secstr_ref)
        #print("MAP SECSTR TARG",map_secstr_targ)

        toadd = []
        for corre in corresp:
            lista_res_targ = graph_targ.vs[map_secstr_targ[tuple(corre[1][1][2:4])]]["reslist"]
            central = [c for c,d in enumerate(lista_res_targ) if tuple(d[2:4])==tuple(corre[1][1][2:4])][0]
            sublist_ref = graph_ref.vs[map_secstr_ref[tuple(corre[0][1][2:4])]]["reslist"]
            start = central-corre[0][0][1]
            fine = central+(corre[0][0][2]-corre[0][0][1])
            add_at_start = 0
            add_at_fine = 0
            if start < 0:
                add_at_start = abs(start)
                start = 0
            if fine > len(lista_res_targ):
                add_at_fine = fine-len(lista_res_targ)
                fine = len(lista_res_targ)
            sublist_tar = lista_res_targ[start:fine]
            if len(sublist_ref) != len(sublist_tar):
                # print("CORRE", corre)
                # print("LISTA RES TARG", lista_res_targ)
                # print("CENTRAL", central)
                # print("SUBLIST REF", sublist_ref)
                # print("START", start, "FINE", fine)
                # print("START", start, "FINE", fine, "START ADD", add_at_start, "FINE ADD", add_at_fine)
                # print("SUBLIST TARG", sublist_tar)
                if add_at_start > 0 and add_at_fine > 0:
                    sublist_tar = sublist_tar+[sublist_tar[-1] for _ in range(add_at_start)]
                    sublist_tar = sublist_tar+[sublist_tar[-1] for _ in range(add_at_fine)]
                elif add_at_start == 0:
                    libre = start
                    if add_at_fine > libre:
                        sublist_tar = sublist_tar+lista_res_targ[0:libre]
                        sublist_tar = sublist_tar+[sublist_tar[-1]for _ in range(add_at_fine-libre)]
                    else:
                        sublist_tar = sublist_tar+lista_res_targ[libre-add_at_fine:libre]
                elif add_at_fine == 0:
                    libre = len(lista_res_targ)-fine
                    if add_at_start > libre:
                        sublist_tar = sublist_tar+lista_res_targ[fine:]
                        sublist_tar = sublist_tar+[sublist_tar[-1] for _ in range(add_at_start-libre)]
                    else:
                        sublist_tar = sublist_tar+lista_res_targ[fine:fine+add_at_start]

                #print("SUBLIST TAR CORRECTED",sublist_tar)
                if len(sublist_ref) != len(sublist_tar):
                    print("ERROR: they should be of the same size")
                    print(sublist_ref)
                    print(sublist_tar)
                    sys.exit(1)
            toadd.append(zip(sublist_ref,sublist_tar))

        for iterate in toadd:
            for sr,st in iterate:
                found = False
                for key in distance_hash2:
                    if key[1:4] == tuple(sr[1:4]):
                        for q,vlo in enumerate(distance_hash2[key]):
                            if vlo[1][1:4] == tuple(st[1:4]):
                                distance_hash2[key] = distance_hash2[key][q]
                                found = True
                                break
                        if found:
                            break

        # for k,v, in distance_hash2.items():
        #      print(k,v)
        # quit()

    distance_hash = distance_hash2
    # for key,value in distance_hash.items():
    #      print("--",key,value)

    allAtoms = []

    if recompute_rmsd:
        l1 = sorted(distance_hash.keys(), key=lambda x: x[1])
        lit1 = [distance_hash[c1][2] for c1 in l1]
        lit2 = [distance_hash[c1][3] for c1 in l1]
        if len(lit1) > 0 and len(lit1) == len(lit2):
            allatoms_ana = [atm for res in list_CA2 for atm in res.get_parent()]
            allAtoms, rmsd, R, t = get_rmsd_and_RT(lit1, lit2, allatoms_ana)
            allAtoms = [atom for atom in allatoms_ana if atom.get_name().lower() == "ca"]
            return get_CA_distance_dictionary(list_CA1, allAtoms, max_rmsd=max_rmsd if cycle+1 <= cycles else last_rmsd,
                                              recompute_rmsd=True if cycle+1 <= cycles else False, cycle=cycle+1,
                                              get_superposed_atoms=get_superposed_atoms)

    if get_superposed_atoms:
        l1 = sorted(distance_hash.keys(), key=lambda x: x[1])
        lit1 = [distance_hash[c1][2] for c1 in l1]
        lit2 = [distance_hash[c1][3] for c1 in l1]
        distance_hash = {key: distance_hash[key][:-2] for key in distance_hash}
        if len(lit1) > 0 and len(lit1) == len(lit2):
            allatoms_ana = [atm for res in list_CA2 for atm in res.get_parent()]
            allAtoms, rmsd, R, t = get_rmsd_and_RT(lit1, lit2, allatoms_ana)
            allAtoms = [atom for atom in allatoms_ana if atom.get_name().lower() == "ca"]
            return distance_hash, allAtoms, rmsd
        else:
            return distance_hash, list_CA2, rmsd
    else:
        distance_hash = {key: distance_hash[key][:-2] for key in distance_hash}
        return distance_hash

def get_rmsd_and_RT(ca_list1,ca_list2,full_ca, transform=True, n_iter=5):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param ca_list1:
    :type ca_list1:
    :param ca_list2:
    :type ca_list2:
    :param full_ca:
    :type full_ca:
    :return:
    :rtype:
    """
    #structure1 = get_structure("cmp2", reference)
    #full_ca = [residue['CA'] for residue in Bio.PDB.Selection.unfold_entities(structure1, 'R')]

    atom_list_a = [atom.get_coord() if hasattr(atom,"get_coord") else atom for atom in ca_list1]
    atom_list_b = [atom.get_coord() if hasattr(atom,"get_coord") else atom for atom in ca_list2]
    atom_list_a = numpy.asarray(atom_list_a)
    atom_list_b = numpy.asarray(atom_list_b)
    transf, rmsd_list = csb.bio.utils.fit_wellordered(atom_list_a, atom_list_b, n_iter=n_iter, full_output=True,
                                                             n_stdv=2, tol_rmsd=0.005, tol_stdv=0.0005)
    if len(rmsd_list) > 0:
        rmsd = rmsd_list[-1][1]
    else:
        rmsd = 100

    R, t = transf
    #print("---",full_ca[0].get_full_id(),full_ca[0].get_coord())
    if transform:
        allAtoms = transform_atoms(full_ca, R, t)
        return allAtoms,rmsd,R,t
    else:
        return rmsd,R,t


def get_rmsd(coords1,coords2):
    diff = coords1 - coords2
    return numpy.sqrt(numpy.sum(numpy.sum(diff * diff, axis=1)) / coords1.shape[0])


def get_rmsd_from_distance_hash(distance_hash):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param distance_hash:
    :type distance_hash:
    :return: rmsd
    :rtype: float
    """
    summatory = 0
    for key in distance_hash.keys():
        summatory=summatory+distance_hash[key][0]
    n = len(distance_hash)
    rmsd = numpy.sqrt(summatory/n)
    return rmsd


def generate_secondary_structure_record(g):
    """ Generate the HELIX/SHEET record in pdb format from a graph. First, will be described all the helices and then
    the beta sheets. Beta-strands of the same sheet will be sorted by their position in space, not by their sequence.

    :author: Ana del Rocío Medina Bernal
    :email: ambcri@ibmb.csic.es
    :param g: graph where each node is a secondary structure and the edges are the geometrical relations between them
    :type g: igraph.Graph
    :return: pdbsearchin
    :rtype pdbsearchin: str
    """

    pdbsearchin = ""
    ah = sorted((x for x in g.vs if x['sstype'] == 'ah'), key=lambda y: y['reslist'][0][3][1])

    try:
        bs_0 = sorted((x for x in g.vs if x['sstype'] == 'bs'),
                      key=lambda y: y['sheet'])  # Try to sort by number of sheet

    except: #If there is some sheet=None or sheet attribute does not exist
        bs_0 = [x for x in g.vs if x['sstype'] == 'bs']
        no_sheet= 1000
        none_sheet = 2000
        for fragment in bs_0:
            if not 'sheet' in fragment.attributes(): # If no sheet attribute
                fragment['sheet'] = no_sheet
                no_sheet += 1
            if fragment['sheet'] == None: # If sheet attribute is None
                fragment['sheet'] = none_sheet
                none_sheet += 1
    bs_0 = sorted((x for x in bs_0 if x['sstype'] == 'bs'),
                  key=lambda y: y['sheet'])  # Sort in case there is a bs with a fragment sheet different from 1000

    coil = sorted((x for x in g.vs if x['sstype'] == 'coil'), key=lambda y: y['reslist'][0][3][1])

    if len(bs_0) > 0:
        current_sheet = bs_0[0]['sheet']
    bs = []
    bs_current = []

    for frag in bs_0:  # Sort by sheet id
        if frag['sheet'] == current_sheet:
            bs_current.append(frag)
        else:
            bs.append(bs_current)
            bs_current = [frag]
            current_sheet = frag['sheet']

    bs.append(bs_current) if len(bs_current) > 0 else print('There are no beta-strands')

    final_bs = []

    if len(bs) > 0:
        for sheet in bs:
            n_con = []
            for frag in sheet:  # Calculate number of neighbours in a radious of 10A
                vecino = [x for x in (g.neighborhood(frag.index)) if (
                    g.vs(x)['sheet'] == g.vs(frag.index)['sheet'] and x != frag.index and
                    g.es[g.get_eid(frag.index, x)]['mean'][1] < 10)] #NOTE: Another version of the code had 10 here
                n_con.append([frag, len(vecino)])
            n_con = sorted(n_con, key=lambda y: (y[1], y[0]['reslist'][0][3][1]))

            bs_sort = [[n_con[0][0], 0]]
            n_con.pop(0)

            while len(n_con) > 0:
                for i, element in enumerate(n_con):
                    try:
                        n_con[i][2] = (g.es[g.get_eid(bs_sort[-1][0], element[0])]['mean'])
                    except:
                        n_con[i].append(g.es[g.get_eid(bs_sort[-1][0], element[0])]['mean'])
                    try:
                        if ALEPH.BS_UD_EA[int(g.es[g.get_eid(bs_sort[-1][0], element[0])]['mean'][0])] > ALEPH.BS_UU_EA[
                            int(g.es[g.get_eid(bs_sort[-1][0], element[0])]['mean'][0])]:
                            n_con[i][3] = -1
                        else:
                            n_con[i][3] = 1
                    except:
                        if ALEPH.BS_UD_EA[int(g.es[g.get_eid(bs_sort[-1][0], element[0])]['mean'][0])] > ALEPH.BS_UU_EA[
                            int(g.es[g.get_eid(bs_sort[-1][0], element[0])]['mean'][0])]:
                            n_con[i].append(-1)
                        else:
                            n_con[i].append(1)

                n_con = sorted(n_con, key=lambda y: y[2][1])
                bs_sort.append([n_con[0][0], n_con[0][3]])
                n_con.pop(0)
            final_bs.append(bs_sort)

    serNum = 1
    for frag in ah:
        pdbsearchin += get_helix_line(serNum, "H", ATOAAAMAP[frag["sequence"][0]],
                                      frag["reslist"][0][2], frag["reslist"][0][3][1], frag["reslist"][0][3][2],
                                      ATOAAAMAP[frag["sequence"][-1]],
                                      frag["reslist"][-1][2], frag["reslist"][-1][3][1],
                                      frag["reslist"][-1][3][2], 1, "", len(frag["sequence"]))
        serNum += 1

    for sheet in final_bs:
        strand = 1
        for frag in sheet:
            pdbsearchin += get_sheet_line(strand, "B", len(sheet), ATOAAAMAP[frag[0]["sequence"][0]],
                                          frag[0]["reslist"][0][2], frag[0]["reslist"][0][3][1],
                                          frag[0]["reslist"][0][3][2], ATOAAAMAP[frag[0]["sequence"][-1]],
                                          frag[0]["reslist"][-1][2], frag[0]["reslist"][-1][3][1],
                                          frag[0]["reslist"][-1][3][2], frag[1])
            strand += 1

    return pdbsearchin


def get_structure(name, pdbf, get_header=False):
    """
    Parse and generate a Structure object from a PDB file.

    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param name: name id of the structure
    :type name: str
    :param pdbf: path of the pdb file
    :type pdbf: Union[str,io.TextIOWrapper]
    :return: structure object
    :rtype: Bio.PDB.Structure
    """
    if isinstance(pdbf, io.StringIO):
        pdbf.seek(0)
    elif not os.path.exists(pdbf):
        pdbf = io.StringIO(SystemUtility.py2_3_unicode(pdbf))

    parser = Bio.PDB.PDBParser()
    structure = parser.get_structure(name, pdbf)

    if not get_header:
        return structure

    remarks = ""
    if isinstance(pdbf, io.StringIO):
        pdbf.seek(0)
        remarks = "".join([line for line in pdbf.read().splitlines() if line.startswith("REMARK")])
    elif not os.path.exists(pdbf):
        pdbf = io.StringIO(SystemUtility.py2_3_unicode(pdbf))
        remarks = "".join([line for line in pdbf.splitlines() if line.startswith("REMARK")])
    else:
        with open(pdbf,"r") as c:
            remarks = "".join([line for line in c.read().splitlines() if line.startswith("REMARK")])

    return structure,remarks

def rename_hetatm_and_icode(pdbf):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param pdbf:
    :return:
    """
    allreadlines = None
    with open(pdbf,"r") as f:
        allreadlines = f.readlines()

    for i,line in enumerate(allreadlines):
        if line.startswith("HETATM"):
            line = "ATOM  "+line[6:]
        if line.startswith("HETATM") or line.startswith("ATOM"):
            line = line[:26]+" "+line[27:]
        allreadlines[i] = line

    pdb = "".join(allreadlines)

    with open(pdbf,"w") as f:
        f.write(pdb)


def get_residue(structure, model, chain, residue):
    """
    Retrieve a specific residue from a structure
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure: structure object
    :type structure: Bio.PDB.Structure
    :param model: number of the model id
    :type model: int
    :param chain: chain name
    :type chain: chr
    :param residue: residue id
    :type residue: tuple
    :return: residue object if found or None
    :rtype: Bio.PDB.Residue or None
    """

    lir = [resil for resil in Bio.PDB.Selection.unfold_entities(structure[model][chain], "R") if resil.get_id() == residue]
    if len(lir) > 0:
        return lir[0]
    else:
        # print(model,chain,residue)
        # print()
        # for resil in Bio.PDB.Selection.unfold_entities(structure[model][chain], "R"):
        #     print(resil.get_full_id())
        return None

def get_dictio_resi_to_secstr(graph,structure):
    dic_resi = {tuple(resi[1:-1]):(frag["sstype"],frag.index) for frag in graph.vs for resi in frag["reslist"] if frag["sstype"] in ["ah","bs"]}

    for resi in get_list_of_residues(structure):
        if resi.has_id("CA") and resi.has_id("C") and resi.has_id("O") and resi.has_id("N") and tuple(resi.get_full_id()[1:]) not in dic_resi:
            dic_resi[tuple(resi.get_full_id()[1:])] = ("cc",None)

    return dic_resi

def get_list_of_residues(structure, model=None, sorting=False):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure:
    :param model:
    :return:
    """
    lir = [resil for resil in Bio.PDB.Selection.unfold_entities(structure if model is None else structure[model], "R")]
    if sorting:
        lir = sorted(lir, key=lambda x: x.get_full_id())

    return lir

def get_list_of_atoms(structure, model=None, sorting=False, type_atom=None):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure:
    :param model:
    :return:
    """
    lir = [resil for resil in Bio.PDB.Selection.unfold_entities(structure if model is None else structure[model], "A") if type_atom is None or resil.get_name()==type_atom.upper()]
    if sorting:
        lir = sorted(lir, key=lambda x: x.get_full_id())

    return lir

def get_atom(structure, model, chain, residue, atom):
    """
    Retrieve a specific residue from a structure
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure: structure object
    :type structure: Bio.PDB.Structure
    :param model: number of the model id
    :type model: int
    :param chain: chain name
    :type chain: chr
    :param residue: residue id
    :type residue: tuple
    :return: residue object if found or None
    :rtype: Bio.PDB.Residue or None
    """
    lir = [atoml for atoml in Bio.PDB.Selection.unfold_entities(structure[model][chain][residue], "A") if atoml.get_id() == atom]
    if len(lir) > 0:
        return lir[0]
    else:
        return None


def get_backbone(residue, without_CB=True):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param residue:
    :param without_CB:
    :return:
    """
    if without_CB or not residue.has_id("CB"):
        return [residue["CA"],residue["C"],residue["O"],residue["N"]]
    else:
        return [residue["CA"],residue["C"],residue["O"],residue["N"],residue["CB"]]


def fetch_pdb(pdbid, outputfile):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param pdbid:
    :param outputfile:
    :return:
    """
    tries = 0
    while 1:
        try:
            baseurl = "ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/pdb/pdb" + pdbid + ".ent.gz"
            try:
                urllib.request.urlretrieve(baseurl, outputfile)
            except:
                urllib2.urlopen(baseurl, outputfile)
            finally:
                break
        except:
            SystemUtility.warning("Cannot download " + str(pdbid) + ".pdb . Try again...")
            tries += 1
            if tries > 10:
                break

    pdbf = outputfile
    if tries > 10:
        SystemUtility.warning("Cannot download " + str(pdbid) + ".pdb . Stop trying. Skipping...")
        # raise Exception("Cannot download "+str(pdb)+".pdb . Stop trying. Skipping...")
        # NOTE: TEMPORANEO PDB is not working today
        # pdbf = "/localdata/PDBDB_20160412/"+pdb[1:3]+"/pdb"+pdb+".ent.gz"

    if pdbf.endswith(".gz"):
        fileObj = gzip.GzipFile(pdbf, 'rb');
        fileContent = fileObj.read()
        fileObj.close()
        os.remove(pdbf)
        pdbf = pdbf[:-3]  # elimino estensione .gz
        fou = open(pdbf, "w")
        fou.write(fileContent)
        fou.close()
    if pdbf.endswith(".ent"):
        pdbf2 = pdbf[:-4]  # elimino estensione .ent
        pdbf2 = pdbf2 + ".pdb"
        os.rename(pdbf, pdbf2)
        pdbf = pdbf2
    if os.path.basename(pdbf).startswith("pdb"):
        root, fileu = os.path.split(pdbf)
        pdbf2 = os.path.basename(pdbf)[3:]  # elimino la parola pdb
        pdbf2 = os.path.join(root, pdbf2)
        os.rename(pdbf, pdbf2)
        pdbf = pdbf2
    shutil.move(pdbf, outputfile)


def write_pdb(structure,path):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure:
    :param path:
    :return:
    """
    io = Bio.PDB.PDBIO()
    io.set_structure(structure)
    io.save(path)

@SystemUtility.deprecated('Must be substituted by get_pdb_from_list_of_atoms')
def write_pdb_file_from_list_of_atoms(reference, outputFilename, dictio_chains={}, renumber=False, uniqueChain=False):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param reference:
    :param outputFilename:
    :param dictio_chains:
    :param renumber:
    :param uniqueChain:
    :return:
    """
    pdbString = ""
    numero = 0
    previous = None
    numea = 1
    for item in reference:
        orig_atom_num = item.get_serial_number()
        hetfield, resseq, icode = item.get_parent().get_id()
        segid = item.get_parent().get_segid()
        if renumber:
            hetfield = " "
            orig_atom_num = numea
            numea += 1
            if previous == None or resseq != previous:
                numero += 1
                previous = resseq
                resseq = numero
            elif previous != None:
                resseq = numero
            icode = " "
        if uniqueChain:
            chain_id = "A"
        if item.get_parent().get_full_id() in dictio_chains:
            chain_id = dictio_chains[item.get_parent().get_full_id()]
        else:
            chain_id = item.get_parent().get_parent().get_id()
        resname = item.get_parent().get_resname()
        element = item.get_name()
        pdbString += get_atom_line(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id)
    flu = open(outputFilename, "w")
    flu.write(pdbString)
    flu.close()

def distance_sq(X, Y):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param X:
    :param Y:
    :return:
    """
    return ((numpy.asarray(X) - Y) ** 2).sum(-1)


# def wfit(X, Y, w):
#     """
#     :author: Dr. Massimo Domenico Sammito
#     :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
#     :param X:
#     :param Y:
#     :param w:
#     :return:
#     """
#
#     from numpy.linalg import svd, det
#     from numpy import dot, sum
#
#     ## center configurations
#
#     norm = sum(w)
#     x = dot(w, X) / norm
#     y = dot(w, Y) / norm
#
#     ## SVD of correlation matrix
#
#     V, _L, U = svd(dot((X - x).T * w, Y - y))
#
#     ## calculate rotation and translation
#
#     R = dot(V, U)
#
#     if det(R) < 0.:
#         U[2] *= -1
#         R = dot(V, U)
#
#     t = x - dot(R, y)
#
#     return R, t
#
#
# def xfit(X, Y, n_iter=10, seed=False, full_output=False):
#     """
#     Maximum likelihood superposition of two coordinate arrays. Works similar
#     to U{Theseus<http://theseus3d.org>} and to L{bfit}.
#
#     :author: Dr. Massimo Domenico Sammito
#     :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
#     :param X:
#     :param Y:
#     :param n_iter:
#     :param seed:
#     :param full_output:
#     :return:
#     """
#     if seed:
#         R, t = numpy.identity(3), numpy.zeros(3)
#     else:
#         R, t = fit(X, Y)
#
#     for _ in range(n_iter):
#         data = distance_sq(X, transform(Y, R, t))
#         scales = 1.0 / data.clip(1e-9)
#         R, t = wfit(X, Y, scales)
#
#     if full_output:
#         return (R, t), scales
#     else:
#         return (R, t)
#
#
# def fit(X, Y):
#     """
#     :author: Dr. Massimo Domenico Sammito
#     :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
#
#     :param X:
#     :param Y:
#     :return:
#     """
#
#     from numpy.linalg import svd, det
#     from numpy import dot
#
#     ## center configurations
#
#     x = X.mean(0)
#     y = Y.mean(0)
#
#     ## SVD of correlation matrix
#
#     V, _L, U = svd(dot((X - x).T, Y - y))
#
#     ## calculate rotation and translation
#
#     R = dot(V, U)
#
#     if det(R) < 0.:
#         U[-1] *= -1
#         R = dot(V, U)
#
#     t = x - dot(R, y)
#
#     return R, t


def transform_atoms(atoms, R, t, s=None, invert=False):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param atoms:
    :param R:
    :param t:
    :param s:
    :param invert:
    :return:
    """
    Y = []

    for atom in atoms:
        Y.append(atom.get_coord())

    Y = transform(Y, R, t, s=s, invert=invert)

    for i in range(len(Y)):
        y = Y[i]
        atoms[i].set_coord(y)

    return atoms


def transform(Y, R, t, s=None, invert=False):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param Y:
    :param R:
    :param t:
    :param s:
    :param invert:
    :return:
    """
    if invert:
        x = numpy.dot(Y - t, R)
        if s is not None:
            s = 1. / s
    else:
        x = numpy.dot(Y, R.T) + t
    if s is not None:
        x *= s
    return x
#
# def fit_wellordered(X, Y, n_iter=None, n_stdv=2, tol_rmsd=.5, tol_stdv=0.05, full_output=False):
#     """
#     :author: Dr. Massimo Domenico Sammito
#     :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
#     :param X:
#     :param Y:
#     :param n_iter:
#     :param n_stdv:
#     :param tol_rmsd:
#     :param tol_stdv:
#     :param full_output:
#     :return:
#     """
#
#     from numpy import ones, compress, dot, sqrt, sum, nonzero, std, average
#
#     rmsd_list = []
#
#     rmsd_old = 0.
#     stdv_old = 0.
#
#     n = 0
#     converged = False
#
#     mask = ones(X.shape[0])
#     while not converged:
#         ## find transformation for best match
#         if n_iter == None or n_iter <= 0:
#             R, t = fit(compress(mask, X, 0), compress(mask, Y, 0))
#         else:
#             R, t = xfit(compress(mask, X, 0), compress(mask, Y, 0), n_iter=n_iter)
#
#         ## calculate RMSD profile
#
#         d = sqrt(sum((X - dot(Y, R.T) - t) ** 2, 1))
#
#         ## calculate rmsd and stdv
#
#         rmsd = sqrt(average(compress(mask, d) ** 2, 0))
#         stdv = std(compress(mask, d))
#         # print "Best rmsd",best_rmsd
#         #print("cycle performed and rmsd",rmsd,"stdv",stdv)
#         ## check conditions for convergence
#
#         if stdv < 1e-10: break
#
#         d_rmsd = abs(rmsd - rmsd_old)
#         d_stdv = abs(1 - stdv_old / stdv)
#
#         if d_rmsd < tol_rmsd:
#             if d_stdv < tol_stdv:
#                 converged = 1
#             else:
#                 stdv_old = stdv
#         else:
#             rmsd_old = rmsd
#             stdv_old = stdv
#
#         ## store result
#
#         perc = average(1. * mask)
#
#         # print "N is",n,"n_iter is",n_iter,"rmsd_list",rmsd_list,"mask",mask
#         # if perc < 0.96: break
#         ###if n_iter == 0: break
#
#         ## throw out non-matching rows
#         new_mask = mask * (d < rmsd + n_stdv * stdv)
#         outliers = nonzero(mask - new_mask)
#         rmsd_list.append([perc, rmsd, outliers])
#         mask = new_mask
#
#         perc = average(1. * mask)
#         if n_iter is None or n_iter <= 0 or n >= n_iter: break
#
#         n += 1
#
#     #print("Iter number: ",n)
#
#     if full_output:
#         return (R, t), rmsd_list, rmsd
#     else:
#         return (R, t)
#

def check_continuity(res1, res2, swap=True, verbose=False):
    """
    Check if two residues are continous in a structure. It checks the 3d cordinates not the residue ids.
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param res1: First Residue
    :type res1: Bio.PDB.Residue
    :param res2: Following Residue
    :type res2: Bio.PDB.Residue 
    :return: True if they are cntinous, False if they are not
    :rtype: bool
    """

    try:
        resaN = res2["N"]
        prevResC = res1["C"]
    except:
        return False

    checkCont = numpy.sqrt(((resaN.get_coord()-prevResC.get_coord())**2).sum(axis=0))

    if verbose:
        print("CHECKING",resaN.get_full_id(),prevResC.get_full_id(),checkCont)

    if checkCont <= 1.5:
        return True
    else:
        if swap:
            return check_continuity(res2,res1, swap=False)
        else:
            return False


def get_helix_line(idnumber, idname, restartname, chainstart, restartnumber, resicodestart, resendname, chainend, resendnumber, resicodeend, typehelix, comment, lenhelix):
    """
    For an helix it returns the string formatted representing the HELIX record in the pdb
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param idnumber: index number
    :type idnumber: int
    :param idname: idname
    :type idname: str
    :param restartname: first residue name
    :type restartname: str
    :param chainstart: chain of the first residue
    :type chainstart: chr
    :param restartnumber: number of the first residue
    :type restartnumber: int
    :param resicodestart: icode of the first residue
    :type resicodestart: str
    :param resendname:  name of the last residue
    :type resendname: str
    :param chainend:  chain of the last residue
    :type chainend: chr
    :param resendnumber:  number of the last residue
    :type resendnumber: int
    :param resicodeend: icode of the last residue
    :type resicodeend: str
    :param typehelix:  type of helix (see PDB standard for HELIX)
    :type typehelix: int
    :param comment:  string comment
    :type comment: str
    :param lenhelix: number of reasidues in the helix
    :type lenhelix: int
    :return record: HELIX record
    :rtype record: str 
    """

    HELIX_FORMAT_STRING = "{:<6s} {:>3d} {:>3s} {:>3s} {:1s} {:>4d}{:1s} {:>3s} {:1s} {:>4d}{:1s}{:>2d}{:>30s} {:>5d}"
    return HELIX_FORMAT_STRING.format("HELIX",idnumber,idname,restartname,chainstart,restartnumber,resicodestart,resendname,chainend,resendnumber,resicodeend,typehelix,comment,lenhelix)+"\n"


def get_sheet_line(idnumber, idnamesheet, nofstrandsinsheet, restartname, chainstart, restartnumber, resicodestart, resendname, chainend, resendnumber, resicodeend, sense):
    """
    For a beta strand it returns the string formatted representing the SHEET record in the pdb
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param idnumber: index number
    :type idnumber: int
    :param idnamesheet: idname
    :type idnamesheet: str
    :param nofstrandsinsheet: number of beta strand in the beta sheet
    :type nofstrandsinsheet: int
    :param restartname: first residue name
    :type restartname: str
    :param chainstart: chain of the first residue
    :type chainstart:  chr
    :param restartnumber: number of the first residue
    :type restartnumber: int
    :param resicodestart: icode of the first residue
    :type resicodestart: str
    :param resendname: name of the last residue
    :type resendname: str
    :param chainend: chain for the last residue
    :type chainend: chr
    :param resendnumber: number of the last residue
    :type resendnumber: int
    :param resicodeend:  icode of the last residue
    :type resicodeend: str
    :param sense: direction of the strand (see PDB standard for SHEET)
    :type sense: int
    :return record:  SHEET record
    :rtype record: str 
    """

    SHEET_FORMAT_STRING = "{:<6s} {:>3d} {:>3s}{:>2d} {:>3s} {:1s}{:>4d}{:1s} {:>3s} {:1s}{:>4d}{:1s}{:>2d} {:>4s}{:>3s} {:1s}{:>4s}{:1s} {:>4s}{:>3s} {:1s}{:>4s}{:1s}"
    return SHEET_FORMAT_STRING.format("SHEET",idnumber,idnamesheet,nofstrandsinsheet,restartname,chainstart,restartnumber,resicodestart,resendname,chainend,resendnumber,resicodeend,sense,"","","","","","","","","","")+"\n"


def get_atom_line(atom, element, hetfield, segid, atom_number, resname, resseq, icode, chain_id, normalize=False, bfactorNor=25.00, charge=" ", applyRt=None):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param atom:
    :param element:
    :param hetfield:
    :param segid:
    :param atom_number:
    :param resname:
    :param resseq:
    :param icode:
    :param chain_id:
    :param normalize:
    :param bfactorNor:
    :param charge:
    :return:
    """

    ATOM_FORMAT_STRING = "%s%6i %-4s%c%3s %c%4i%c   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n"

    if hetfield != " ":
        record_type = "HETATM"
    else:
        record_type = "ATOM "

    element = element.strip().upper()
    # print "ELEMENT value was: ",type(element),element
    element = element[0]
    # print "ELEMENT value is: ",type(element),element

    name = atom.get_fullname()
    altloc = atom.get_altloc()

    if applyRt is not None:
        coo = atom.get_coord()
        coo = numpy.array([coo])
        coo = transform(coo, applyRt[0], applyRt[1])
        x, y, z = coo[0]
    else:
        x, y, z = atom.get_coord()

    occupancy = atom.get_occupancy()
    if not normalize:
        bfactor = atom.get_bfactor()
    else:
        bfactor = bfactorNor
    args = (record_type, atom_number, name, altloc, resname, chain_id, resseq, icode, x, y, z, occupancy, bfactor, segid, element, charge)
    ala = ATOM_FORMAT_STRING % args
    if record_type == "HETATM":
        clu = ala.split()
        spaziBianchi = 5 - len(clu[1])
        stri = "HETATM"
        for ulu in range(spaziBianchi):
            stri += " "
        stri += clu[1]
        ala = stri + ala[12:]
    return ala


def get_pdb_from_structure(structure,model):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param structure:
    :param model:
    :return:
    """
    atoms = get_list_of_atoms(structure,model)
    return get_pdb_from_list_of_atoms(atoms, renumber=False, uniqueChain=False, chainId="A", chainFragment=False, diffchain=None, polyala=True, maintainCys=False, normalize=False, sort_reference=True)[0]


def get_pdb_from_list_of_atoms(reference, renumber=False, uniqueChain=False, chainId="A", chainFragment=False,
                               diffchain=None, polyala=True, maintainCys=False, normalize=False, sort_reference=True,
                               remove_non_res_hetatm=False, dictio_chains={}, write_pdb=False, path_output_pdb='', applyRt=None):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param reference:
    :param renumber:
    :param uniqueChain:
    :param chainId:
    :param chainFragment:
    :param diffchain:
    :param polyala:
    :param maintainCys:
    :param normalize:
    :param sort_reference:
    NOTE CM: these parameters have been added by me
    :param remove_non_res_hetatm:
    :param dictio_chains:
    :param write_pdb:
    :return:
    """
    pdbString = ""
    numero = 1
    resn = {}
    nur = 1
    lastRes = None
    prevChain = 0
    lich = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "Z",
            "J", "K", "X", "Y", "W", "a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "m", "n", "o", "p", "q", "r",
            "s", "t", "u", "v", "z", "j", "k", "x", "y", "w", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    # if chainFragment or uniqueChain:
    #   renumber = True

    if remove_non_res_hetatm:
        reference = [atm for atm in reference if atm.get_parent().get_resname().upper() in AAList]

    if not polyala:
        reference = [atm for res in reference for atm in res.get_parent()]
    elif maintainCys:
        reference = [atm if res.get_resname().lower() == "cys" else res for res in reference for atm in res.get_parent()]

    if polyala:
        reference = [atm for atm in reference if atm.get_name().lower() in ["ca", "c", "o", "n", "cb"]]

    if sort_reference:
        reference = Bio.PDB.Selection.uniqueify(reference)
        listore = sorted(reference, key=lambda x:  x.get_full_id())
    else:
        listore = reference

    for item in listore:

        #print(item.get_full_id())
        #if item.get_full_id() in set(seen):
        #    continue

        #seen.append(item.get_full_id())
        orig_atom_num = item.get_serial_number()
        hetfield, resseq, icode = item.get_parent().get_id()
        segid = item.get_parent().get_segid()
        chain_id = item.get_parent().get_parent().get_id()
        hetfield = " "
        if (resseq, chain_id) not in resn.keys():
            if lastRes != None:
                # print "Checking Continuity",lastRes.get_parent().get_full_id(),item.get_parent().get_full_id(),checkContinuity(lastRes.get_parent(),item.get_parent())
                # print "Checking Continuity",item.get_parent().get_full_id(),lastRes.get_parent().get_full_id(),checkContinuity(item.get_parent(),lastRes.get_parent())
                # print lich[prevChain]
                # print
                if not check_continuity(lastRes.get_parent(), item.get_parent()):
                    if renumber:
                        #print("LASTRES", lastRes.get_parent().get_full_id(), "ITEM:", item.get_parent().get_full_id())
                        nur += 10
                    if chainFragment:
                        prevChain += 1
            new_chain_id = chain_id
            if dictio_chains!={}:
                new_chain_id=dictio_chains[item.get_parent().get_full_id()]
            elif uniqueChain:
                new_chain_id = chainId
            elif chainFragment:
                new_chain_id = lich[prevChain]
            if renumber:
                resn[(resseq, chain_id)] = (nur, new_chain_id)
            else:
                resn[(resseq, chain_id)] = (resseq, new_chain_id)
            lastRes = item
            nur += 1
        tuplr = resn[(resseq, chain_id)]
        resseq = tuplr[0]
        chain_id = tuplr[1]
        icode = " "
        orig_atom_num = numero
        numero += 1

        resname = item.get_parent().get_resname()
        element = item.get_name()
        pdbString += get_atom_line(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id, normalize=normalize, applyRt=applyRt)

    if diffchain != None and len(diffchain) > 0:
        prevChain += 1
        lastRes = None
        for item in diffchain:
            orig_atom_num = item.get_serial_number()
            hetfield, resseq, icode = item.get_parent().get_id()
            segid = item.get_parent().get_segid()
            chain_id = item.get_parent().get_parent().get_id()
            hetfield = " "
            if (resseq, chain_id) not in resn.keys():
                if lastRes != None:
                    if not check_continuity(lastRes.get_parent(), item.get_parent()):
                        if renumber:
                            #print("LASTRES",lastRes.get_parent().get_full_id(),"ITEM:",item.get_parent().get_full_id())
                            nur += 10
                        if chainFragment:
                            prevChain += 1
                new_chain_id = chain_id
                if uniqueChain:
                    new_chain_id = chainId
                elif chainFragment:
                    new_chain_id = lich[prevChain]

                if renumber:
                    resn[(resseq, chain_id)] = (nur, new_chain_id)
                else:
                    resn[(resseq, chain_id)] = (resseq, new_chain_id)
                lastRes = item
                nur += 1
            tuplr = resn[(resseq, chain_id)]
            resseq = tuplr[0]
            chain_id = tuplr[1]
            icode = " "
            orig_atom_num = numero
            numero += 1

            resname = item.get_parent().get_resname()
            element = item.get_name()
            pdbString += get_atom_line(item, element, hetfield, segid, orig_atom_num, resname, resseq, icode, chain_id, normalize=normalize, applyRt=applyRt)

    if write_pdb:
        fichmodel=open(path_output_pdb,'w')
        fichmodel.write(pdbString)
        fichmodel.close()
    return pdbString, resn


def get_pdb_from_list_of_frags(nModel, allfrags, structure, pathBase, dizioConv={}, externalRes=[], normalize=False):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param nModel:
    :param allfrags:
    :param structure:
    :param pathBase:
    :param dizioConv:
    :param externalRes:
    :param normalize:
    :return:
    """
    atoms = []
    for frag in allfrags:
        for resi in frag["reslist"]:
            atoms += get_backbone(get_residue(structure, resi[1], resi[2], resi[3]),without_CB=False)

    pdb_string, dict_conv = get_pdb_from_list_of_atoms(atoms,normalize=normalize)

    pdbid = str(structure.get_id())
    nomeFilefine = pathBase + "/" + pdbid + "_"

    for y in range(len(allfrags)):
        fragment = allfrags[y]
        for i in range(len(fragment["resIdList"])):
            re = fragment["resIdList"][i]
            if i == 0:
                if len(dizioConv.keys()) > 0:
                    nomeFilefine += str((dizioConv[(fragment["chain"], re, "CA")])[1]) + "*" + str(fragment["fragLength"])
                else:
                    nomeFilefine += str(re[1]) + str(re[2])
            if y != (len(allfrags) - 1) and i == 0:
                nomeFilefine += "_"
            elif y == (len(allfrags) - 1) and i == 0:
                if nModel != "":
                    nomeFilefine += "_" + nModel

    pdbString = ""
    pdbString += "REMARK TITLE " + nomeFilefine + "\n"
    pdb_string = pdbString+pdb_string

    return (nomeFilefine, pdb_string, dict_conv)


def read_pdb_ss_information_return_list_dics (input_pdb_file):
    """ Reads the pdb and collects the information about each HELIX and SHEET record in a list

    :author: Ana Medina
    :email: ambcri@ibmb.csic.es

    :param input_file_pdb: pdb file with the ss annotation
    :type input_pdb_file: str
    :return list_file_all: list containing a dictionary for each aa presented in a ss
    :rtype list_file_all: list
    :return False: In case no remark was found
    :rtype: bool
    """

    pdbfile = open(input_pdb_file)
    file_lines=pdbfile.readlines()
    pdbfile.close()
    list_file_all=[] #List with dictionaries. Each dictionary correspond to each ss element of the pdb file

    def catch_substring(a, b, line):
        try:
            return line[a:b].strip()
        except:
            return ""

    for line in file_lines:
        dic_var = {}
        dic_var['ss']= line[0:6].strip()
        if dic_var['ss'] == 'HELIX':
            dic_var['ser_num'] = int(catch_substring(7, 10, line)) #Serial number of the helix. This starts at 1 abd increases incrementally
            dic_var['helix_id'] = catch_substring(11, 14, line) #Helix identifier. In additio to a serial number, each helix is given and alphanumeric character helix identifier
            dic_var['init_res_name'] = catch_substring(15, 18, line) #Name of the initial residue
            dic_var['init_chain_id'] = catch_substring(19, 20, line) #Chain identifier for the chain containing this helix
            dic_var['init_seq_num'] = int(catch_substring(21, 25, line)) #Sequence number of the initial residue
            dic_var['init_i_code'] = catch_substring(25, 26, line) #Insertion code of the initial residue
            dic_var['end_res_name'] = catch_substring(27, 30, line) #Name of the terminal residue of the helix
            dic_var['end_chain_id'] = catch_substring(31, 32, line) #Chain identifier fot the chain containing this helix
            dic_var['end_seq_num'] = int(catch_substring(33, 37, line)) #Sequence number of the terminal residue
            dic_var['end_i_code'] = catch_substring(37, 38, line) #Insertion code of the terminal residue
            dic_var['helix_class'] = int(catch_substring(38, 40, line)) #Helix class (see ftp://ftp.wwpdb.org/pub/pdb/doc/format_descriptions/Format_v33_A4.pdf)
            dic_var['comment'] = catch_substring(40, 70, line) #Comment about this helix
            dic_var['length'] = int(catch_substring(71, 76, line)) #Length of this helix
            list_file_all.append(dic_var)
        elif dic_var['ss'] == 'SHEET':
            dic_var['strand'] = int(catch_substring(7, 10, line)) #Strand number which starsts aty 1 fot each strand within a sheet and increases by one
            dic_var['sheet_id'] = catch_substring(11, 14, line) #Sheet identifier
            dic_var['num_strands'] = int(catch_substring(14, 16, line)) #Number of strands in sheet
            dic_var['init_res_name'] = catch_substring(17, 20, line) #Residue name of initial residue
            dic_var['init_chain_id'] = catch_substring(21, 22, line) #Chain identifier of initial residue in strand
            dic_var['init_seq_num'] = int(catch_substring(22, 26, line)) #Sequence number of initial residue in strand
            dic_var['init_i_code'] = catch_substring(26, 27, line) #Insertion code of initial residue in strand
            dic_var['end_res_name'] = catch_substring(28, 31, line) #Residue name of terminal residue
            dic_var['end_chain_id'] = catch_substring(32, 33, line) #Chain identifier of terminal residue
            dic_var['end_seq_num'] = int(catch_substring(33, 37, line)) #Sequence number of terminal residue
            dic_var['end_i_code'] = catch_substring(37, 38, line) #Insertion code of terminal residue
            dic_var['sense'] = int(catch_substring(38, 40, line)) #Sense of strand with respect to previous strand in the sheet. 0 if first strand, 1 if parallel, and -1 if anti-parallel
            dic_var['cur_atom'] = catch_substring(41, 45, line) #Registration. Atom name in current strand
            dic_var['cur_res_name'] = catch_substring(45, 48, line) #Registration. Residue name in current strand
            dic_var['cur_chain_id'] = catch_substring(49, 50, line) #Registration. Chain identifier in current strand
            dic_var['cur_res_seq'] = catch_substring(50, 54, line) #Residue sequence number in current strand
            dic_var['cur_i_code'] = catch_substring(54, 55, line) #Registration. Insertion code in current strand
            dic_var['prev_atom'] = catch_substring(56, 60, line) #Registration. Atom name in previous strand
            dic_var['prev_res_name'] = catch_substring(60, 63, line) #Registration. Residue name in previous strand
            dic_var['prev_chain_id'] = catch_substring(64, 65, line) #Registration. Chain identifier in previous strand
            dic_var['prev_res_seq'] = catch_substring(65, 69, line) #Registration. Residue sequence number in previous strand
            dic_var['prev_i_code'] = catch_substring(69, 70, line) #Registration. Insertion code in previous strand
            list_file_all.append(dic_var)
        if len (list_file_all) == 0:
            return False
        else:
            return list_file_all

def shredder_template_annotation(model_file, current_directory, bfacnorm=True, poliA=True, cys=False, remove_coil=True,
                                 nres_extend=0, min_alpha=7, min_beta=4, min_diff_ah=0.45, min_diff_bs=0.2,
                                 gyre_preserve_chains=False, algorithm_community='fastgreedy',
                                 pack_beta_community=False, homogenity_community=False):
    """

    :author: Claudia Millan
    :email: cmncri@ibmb.csic.es


    :param model_file: path to the pdb file to process
    :type model_file: str
    :param current_directory: path of the current working directory
    :type current_directory: str
    :param bfacnorm: indicates whether to perform or not a bfactor normalization (default True)
    :type bfacnorm: boolean
    :param poliA: indicates whether to convert the model to only mainchain atoms (default True)
    :type poliA: boolean
    :param cys: indicates whether to leave or not cysteine residues untouched even if poliA is True (default False)
    :type cys: boolean
    :param remove_coil: indicates whether to leave the coil in the template or not (default True)
    :type remove_coil: boolean
    :param nres_extend: number of residues to add to secondary structure elements in the partial_coil case
    :type nres_extend: int
    :param min_alpha: minimum size in residues for any given helix in the template to be considered
    :type min_alpha: int
    :param min_beta: minimum size in residues for any given beta strand in the template to be considered
    :type min_beta: int
    :param min_diff_ah:
    :type min_diff_ah:
    :param min_diff_bs:
    :type min_diff_bs:
    :param gyre_preserve_chains:
    :type gyre_preserve_chains:
    :param algorithm_community:
    :type algorithm_community:
    :param pack_beta_community:
    :type pack_beta_community:
    :param homogenity_community:
    :type homogenity_community:

    :return dict_oristru: dictionary with keys being each residue number, and the following structure
             dict_template[nres] = {'residue_object': BioPython residue object,
                          'ori_full_id': tuple, 'ori_chain': str, 'ori_nres': int,'ori_nameres': str,
                          'ss_type_res': str (can be ah,bs,coil), 'ss_reslist': list, 'ss_id_res': str,
                          'first_ref_cycle_group': str, 'second_ref_cycle_group': str,'third_ref_cycle_group': str}
    :rtype dict_oristru: dict
    :return model_file: path to the modified template file
    :rtype model_file: str
    :return distance_matrix_CA:
    :rtype distance_matrix_CA: list of lists
    :return names_matrix:
    :rtypenames_matrix: list
    """

    print("\nARCIMBOLDO_SHREDDER template treatment and annotation has started:")
    print("\n Processing ", model_file)

    # Prepare the input pdb file
    rename_hetatm_and_icode(model_file)
    parser = Bio.PDB.PDBParser()
    oristru_name = os.path.basename(model_file)[:-4]
    oristru = parser.get_structure(os.path.basename(model_file)[:-4], model_file)
    list_atoms = Bio.PDB.Selection.unfold_entities(oristru, 'A')

    dictio_chainid = {}
    # check the chain id for the case in which it might be empty
    set_chain_id = set([ atom.get_full_id()[2] for atom in list_atoms])
    if (len(set_chain_id)==1 and set_chain_id == set([' '])) or (len(set_chain_id) > 1 and not gyre_preserve_chains):
        for model in oristru:
            for chain in model:
                for residue in chain:
                    key_chain = residue.get_full_id()  # that is the key for the dictio_chains dictionary
                    try:
                        dictio_chainid[key_chain] = 'A'
                    except:
                        print('Some error happened')
                        sys.exit(0)

    if len(set_chain_id)==1 and not gyre_preserve_chains: # unique chain, we want to keep it the original
        unique_chain_id=(list(set_chain_id))[0]
        for model in oristru:
            for chain in model:
                for residue in chain:
                    key_chain = residue.get_full_id()  # that is the key for the dictio_chains dictionary
                    try:
                        dictio_chainid[key_chain] = unique_chain_id
                    except:
                        print('Some error happened')
                        sys.exit(0)

    pdb_string, dict_conv = get_pdb_from_list_of_atoms(list_atoms, renumber=True, polyala=poliA, maintainCys=cys,
                                                       normalize=bfacnorm, sort_reference=True,
                                                       remove_non_res_hetatm=True, write_pdb=True,
                                                       dictio_chains=dictio_chainid,
                                                       path_output_pdb=model_file)

    # 3) Get the secondary and tertiary structure description with ALEPH
    graph_template, \
    oristru, \
    matrix, \
    cvs_list, \
    highd = ALEPH.annotate_pdb_model_with_aleph(pdb_model=model_file, weight="distance_avg", min_ah=min_alpha,
                                                min_bs=min_beta, write_pdb=True, strictness_ah=min_diff_ah,
                                                strictness_bs=min_diff_bs, peptide_length=3, is_model=False,
                                                only_reformat=True)
    graph_template = graph_template.vs.select(sstype_in=["ah","bs"]).subgraph()
    iterator_frag = ALEPH.get_all_fragments(graph_template)  # get only ah and bs, I will annotate coil later


    # 4) Open the pdb and populate the dictionary with the residues as keys and saving some information
    if len(Bio.PDB.Selection.unfold_entities(oristru, 'M')) > 1:
        print("\n Sorry, currently the use of NMR models is not supported in ARCIMBOLDO_SHREDDER")
        sys.exit(1)
    listres_oristru = Bio.PDB.Selection.unfold_entities(oristru, 'R')
    dict_oristru = {}
    for i, res in enumerate(listres_oristru):
        tuple_id = res.get_full_id()
        chain = tuple_id[2]
        nres = tuple_id[3][1]
        nameres = res.get_resname()

        dict_oristru[nres] = {'residue_object': res, 'ori_full_id': tuple_id, 'ori_chain': chain, 'ori_nres': nres,
                              'ori_nameres': nameres, 'ss_type_res': None, 'ss_reslist': None, 'ss_id_res': None,
                              'first_ref_cycle_group': None, 'second_ref_cycle_group': None,
                              'third_ref_cycle_group': None}

    # NOTE: At the moment, cycles correspond to:
    # first cycle: community clustering groups
    # second cycle: helices independent and beta strands as they were left by the community clustering
    # third cycle : same as second, but it is not performed by default

    # Get the total number of residues now, to compare later one how many are within secondary structure elements
    total_res = len(listres_oristru)
    print('\n Total number of residues in the input template is', total_res)

    # 5) Now we need to do the community clustering and populate the dict_oristru with the information
    if remove_coil and not gyre_preserve_chains:  # only then we want to annotate in groups
        vclust = ALEPH.get_community_clusters_one_step(algo=algorithm_community, graph_input_d=graph_template,
                                                       structure=oristru, pdb_search_in='', pathpdb='check',
                                                       write_pdb=True, pack_beta_sheet=pack_beta_community,
                                                       homogeneity=homogenity_community)
        if homogenity_community:
            vclust=vclust[0]
        results_community = ALEPH.get_dictionary_from_community_clusters(graph=graph_template, vclust=vclust,
                                                                         structure=oristru, writePDB=False,
                                                                         outputpath=None, header="",
                                                                         returnPDB=False, adding_t=0)

        list_groups = [results_community[key] for key in results_community.keys()]
        unique_community_groups = len(set(list_groups))

    print("\n Found ", len(iterator_frag), " secondary structure elements")
    listres_to_keep = []
    count_extra=0
    for i, dictio in enumerate(iterator_frag):
        # dictio is really a igraph.Vertex, but can be accessed as a dictionary. There is a dictio per fragment
        identifier_ss = dictio["sstype"] + str(i)
        if dictio["sstype"] == 'ah' or dictio["sstype"] == 'bs':
            filterlist = map(lambda x: tuple(x[:-1]), dictio["reslist"])
            print("\n     This is a ", dictio["sstype"], " of ", len(filterlist), " residues --> ",dictio['sequence'])
            if dictio["sstype"] == 'bs':
                print('Beta strands belong to beta sheet id ',dictio["sheet"])
            if (len(filterlist) < min_alpha and dictio["sstype"] == 'ah') or (len(filterlist) < min_beta and dictio["sstype"] == 'bs'):
                continue
            dictio["reslist"]=filterlist # we do not need sequence at this point, we can reduce it to its ids
            filterlist.sort()
            # Check if we need to elongate and how many residues
            if nres_extend != 0:  # only in the partial_coil case
                print('Entering the extension mode in partial_coil')
                # upwards
                first_res_id=filterlist[0][-1][1]
                elong_list_id=[]
                if dict_oristru.has_key(first_res_id-nres_extend):
                    #print '\nwe can extend upwards'
                    for indx in range(first_res_id-nres_extend,first_res_id):
                        # First check if we are entering in another secondary structure
                        if dict_oristru[indx]['ss_type_res']!=None:
                            #print 'We are not free to go, we are accessing another secondary structure'
                            break
                        dict_oristru[indx]['ss_type_res'] = dictio["sstype"]
                        dict_oristru[indx]['ss_id_res'] = identifier_ss
                        dict_oristru[indx]['first_ref_cycle_group']= dict_oristru[first_res_id]['first_ref_cycle_group']
                        dict_oristru[indx]["ori_full_id"]=('stru', dict_oristru[indx]["ori_full_id"][1],
                                                           dict_oristru[indx]["ori_full_id"][2],
                                                           dict_oristru[indx]["ori_full_id"][3])
                        filterlist.append(dict_oristru[indx]["ori_full_id"])
                        filterlist.sort()
                        elong_list_id.append(indx)
                    for indx in elong_list_id: # we want to iterate directly on the ids
                        dict_oristru[indx]['ss_reslist'] = filterlist
                        count_extra = count_extra + 1
                else:
                    continue

                # downwards
                last_res_id=filterlist[-1][-1][1]
                #print 'last_res_id',last_res_id
                if dict_oristru.has_key(last_res_id+nres_extend):
                    #print 'we can extend downwards'
                    #print 'filterlist before',filterlist
                    elong_list_id=[]
                    for indx in range(last_res_id+1,last_res_id+nres_extend+1):
                        #print 'indx',indx
                        #print 'dict_oristru[indx] before',dict_oristru[indx]
                        if dict_oristru[indx]['ss_type_res']!=None:
                            #print 'We are not free to go, we are accessing another secondary structure'
                            break
                        dict_oristru[indx]['ss_type_res'] = dictio["sstype"]
                        dict_oristru[indx]['ss_id_res'] = identifier_ss
                        dict_oristru[indx]['first_ref_cycle_group']= dict_oristru[last_res_id]['first_ref_cycle_group']
                        #print 'dict_oristru[indx] after',dict_oristru[indx]
                        #print 'dict_oristru[indx]["ori_full_id"] before',dict_oristru[indx]["ori_full_id"]
                        dict_oristru[indx]["ori_full_id"]=('stru', dict_oristru[indx]["ori_full_id"][1], dict_oristru[indx]["ori_full_id"][2], dict_oristru[indx]["ori_full_id"][3])
                        #print 'dict_oristru[indx]["ori_full_id"] after ',dict_oristru[indx]["ori_full_id"]
                        filterlist.append(dict_oristru[indx]["ori_full_id"])
                        filterlist.sort()
                        elong_list_id.append(indx)
                    #print 'filterlist after',filterlist
                    for indx in elong_list_id: # we want to iterate directly on the ids
                        dict_oristru[indx]['ss_reslist'] = filterlist
                        count_extra = count_extra + 1
                        #print 'Assigning new ss_reslist to ',indx
                        #print "dict_oristru[indx]['ss_reslist']",dict_oristru[indx]['ss_reslist']
                else:
                    continue
                    #print 'sorry, we can not extend downwards'

            listres_to_keep.extend(filterlist)

            if dictio["sstype"] == 'ah' or dictio["sstype"] == 'bs':
                for j in range(len(filterlist)):
                    key = filterlist[j][3][1]
                    dict_oristru[key]['ss_type_res'] = dictio["sstype"]
                    dict_oristru[key]['ss_id_res'] = identifier_ss
                    dict_oristru[key]['ss_reslist'] = filterlist


    # Annotate the dictionary by groups if community was performed
    if remove_coil and not gyre_preserve_chains:  # only then we want to annotate in groups
        # Check community results
        if unique_community_groups <= 0:
            print('\nWith current community clustering strategy there are no clusters returned, please check')
            sys.exit(1)

        # Get the correct ids to use and annotate groups for gyre and gimble
        list_used_ids=[]
        for key in sorted(results_community.keys()):
            tuple_id = key
            nres = tuple_id[3][1]
            dict_oristru[nres]['first_ref_cycle_group'] = results_community[key]
            ide = int(results_community[key].split("group")[1])
            if ide not in list_used_ids:
                list_used_ids.append(ide)
        list_used_ids.sort()
        last_used_id = list_used_ids[-1]

        # Perform the annotation for the other two levels
        number_id = last_used_id
        for i, dictio in enumerate(iterator_frag):
            print('\n Processing element ',i,' that corresponds to ',dictio)
            if dictio["sstype"] == 'ah':
                number_id += 1  # next group
                print('This is an alpha helix formed by ',dictio["reslist"])
                for j in range(len(dictio["reslist"])):
                    key = dictio["reslist"][j][3][1]
                    dict_oristru[key]['third_ref_cycle_group'] = 'group' + str(number_id)  # helices are treated independently in both second and third cycle grouping
                    dict_oristru[key]['second_ref_cycle_group'] = 'group' + str(number_id)
            elif dictio["sstype"] == 'bs':
                print('This is a beta strand formed by ',dictio["reslist"])
                number_id += 1  # next group
                for j in range(len(dictio["reslist"])):
                    key = dictio["reslist"][j][3][1]
                    dict_oristru[key]['third_ref_cycle_group'] = 'group' + str(number_id)  # one per beta strand
                    dict_oristru[key]['second_ref_cycle_group'] = dict_oristru[key]['first_ref_cycle_group'] # this will keep the same beta community as in the first grouping

    # 6) If remove_coil has been set, remove that residues from the model and the dictionary
    if remove_coil:
        for model in oristru.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    id_res = residue.get_full_id()
                    mini_id = residue.id
                    nres = mini_id[1]
                    if id_res not in listres_to_keep:
                        chain.detach_child(mini_id)
                        dict_oristru.pop(nres, None)
                    if nres in dict_oristru and dict_oristru[nres]['first_ref_cycle_group'] is None:
                        chain.detach_child(mini_id)
                        dict_oristru.pop(nres, None)
    # NOTE CM: I am filtering out the coil residues from the graph, so I need this to annotate them
    # NOTE CM: At the moment they are annotated as single residues. Possibly doing it in continuous regions better
    else:
        count_coil = 0
        for model in oristru.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    id_res = residue.get_full_id()
                    mini_id = residue.id
                    nres = mini_id[1]
                    if dict_oristru[nres]['ss_type_res'] is None:
                        dict_oristru[nres]['ss_type_res'] = 'coil'
                        dict_oristru[nres]['ss_id_res'] = 'coil'+str(count_coil)
                        dict_oristru[nres]['ss_reslist'] = [id_res]
                        count_coil += 1

    if remove_coil and not gyre_preserve_chains:
        # Check if community clustering has assigned all residues in case we did it
        # Two possibilities: there is a problem with the distances or we extended the secondary structure elements
        if len(results_community) < len(dict_oristru.keys()) and nres_extend != 0:
            # it is normal that we don't have the same, check if the difference correspond to the number of added residues
            if len(results_community) + count_extra == len(dict_oristru.keys()):
                print('\n We are fine, we added extra ',count_extra,' residues ', ' Keep going ')
            else:
                print(colored("FATAL:", "red"), colored(
                "Community clustering did not asign a group to all residues, please consider modifying distances values for the community_clustering",
                'yellow'))
                sys.exit(1)
        elif len(results_community) < len(dict_oristru.keys()) and nres_extend == 0:
            if not gyre_preserve_chains: # in that case we are not going to consider community clustering groups
                print(colored("FATAL:", "red"), colored("Community clustering did not asign a group to all residues, please consider modifying distances values for the community_clustering",'yellow'))
                sys.exit(1)
        else:
            print('\nAll OK, Super!')

    # Check % of secondary structure
    ss_percentage=float(len(listres_to_keep))/total_res*100
    print('\n The percentage of secondary structure for this template is ',ss_percentage)
    if ss_percentage < 50:
        print(colored("""\nWARNING: With less than 50 per cent of secondary structure present in the template, it would be better to run ARCIMBOLDO_SHREDDER with the full template without removing the coil """,'yellow'))
    else:
        print(colored("\nMore than 50 per cent of the structure has secondary structure, continuing with the run", "magenta"))

    # 5) Write the processed template to generate the models
    # Even the not gyre_preserve_chains condition has been checked before
    if not gyre_preserve_chains and remove_coil:
        print(colored("\nRemove coil has been set to on, and gyre and gimble will be performed according to automatic annotation", "magenta"))
        list_atoms = Bio.PDB.Selection.unfold_entities(oristru, 'A')
        list_atoms=sorted(list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        get_pdb_from_list_of_atoms(reference=list_atoms,renumber=False, uniqueChain=False, chainId='A',
                                   chainFragment=False, polyala=False, maintainCys=False,
                                   normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={},
                                   write_pdb=True, path_output_pdb=outpdbpath)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))

    if not gyre_preserve_chains and not remove_coil:
        print(colored("\nCoil has been left in the template model and no gyre or gimble refinement will be performed"
        , "magenta"))
        list_atoms = Bio.PDB.Selection.unfold_entities(oristru, 'A')
        list_atoms=sorted(list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        get_pdb_from_list_of_atoms(reference=list_atoms,renumber=False, uniqueChain=False, chainId='A',
                                   chainFragment=False, polyala=False, maintainCys=False,
                                   normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={},
                                   write_pdb=True, path_output_pdb=outpdbpath)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))

    if gyre_preserve_chains and remove_coil:
        print(colored("\nRemove coil has been set to on, and gyre and gimble will be performed according to user-given annotation", "magenta"))
        # save the model without the coil but with the chain it had at the beginning
        list_atoms = Bio.PDB.Selection.unfold_entities(oristru, 'A')
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        list_atoms=sorted(list_atoms,key=lambda x:x.get_parent().get_full_id()[3][1]) # sort by residue number
        get_pdb_from_list_of_atoms(reference=list_atoms,renumber=False, uniqueChain=False, chainId="A",
                                   chainFragment=False, polyala=False, maintainCys=False,
                                   normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={},
                                   write_pdb=True, path_output_pdb=outpdbpath)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))
    if gyre_preserve_chains and not remove_coil:
        print(colored("\nThe coil has been left, and gyre and gimble will be performed according to user-given annotation", "magenta"))
        # save model with the coil but making sure non-annotated residues are not considered. Keep chains user-given
        list_atoms = Bio.PDB.Selection.unfold_entities(oristru, 'A')
        outpdbpath = os.path.join(current_directory, "shred_template.pdb")
        list_atoms = sorted(list_atoms, key=lambda x: x.get_parent().get_full_id()[3][1])  # sort by residue number
        get_pdb_from_list_of_atoms(reference=list_atoms,renumber=False, uniqueChain=False, chainId="A",
                                   chainFragment=False, polyala=False, maintainCys=False,
                                   normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={},
                                   write_pdb=True, path_output_pdb=outpdbpath)
        model_file = os.path.abspath(os.path.join(current_directory, "shred_template.pdb"))

    # Write the pdbs with their grouping levels to check
    if remove_coil and not gyre_preserve_chains:
        path_pdbfirst=os.path.join(current_directory,oristru_name+'_first_grouping_level.pdb')
        shutil.copy(model_file,path_pdbfirst)
        modify_chains_according_to_shredder_annotation(pdb=path_pdbfirst, dictio_annotation=dict_oristru,
                                       annotation_level='first_ref_cycle_group', output_path=current_directory)
        path_pdbsecond=os.path.join(current_directory,oristru_name+'_second_grouping_level.pdb')
        shutil.copy(model_file,path_pdbsecond)
        modify_chains_according_to_shredder_annotation(pdb=path_pdbsecond, dictio_annotation=dict_oristru,
                                       annotation_level='second_ref_cycle_group', output_path=current_directory)


    # 6) Get the distance matrix between the CA
    distance_matrix_CA, names_matrix = get_CA_distance_matrix(model_file)

    # 7) Save annotation in a pkl file
    save_annotation=open(os.path.join(current_directory,'annotated_template.pkl'),'wb')
    pickle.dump(dict_oristru,save_annotation)
    save_annotation.close()

    return model_file, dict_oristru, distance_matrix_CA, names_matrix, ss_percentage


def normalize_bfactors_of_pdb(pdbf, bf):
    """
    :author: Dr. Massimo Domenico Sammito
    :email: msacri@ibmb.csic.es / massimo.sammito@gmail.com
    :param pdbf:
    :type pdbf:
    :param bf:
    :type bf:
    :return:
    :rtype:
    """
    f = open(pdbf, "r")
    linee = f.readlines()
    f.close()

    f2 = open(pdbf, "w")
    bf = ("%.2f" % bf)
    if len(bf) <= 5:
        bf = ' ' + bf
    for linea in linee:
        if not linea.startswith("ATOM") and not linea.startswith("HETATM"):
            f2.write(linea)
        else:
            li = linea.split()
            lou = list(linea)
            lou[60] = bf[0]
            lou[61] = bf[1]
            lou[62] = bf[2]
            lou[63] = bf[3]
            lou[64] = bf[4]
            lou[65] = bf[5]
            mio = ''.join(lou)
            mio = mio.strip()
            f2.write(mio + "\n")
    f2.close()


def trim_sidechains_and_cysteines(pdb_model, poliA, cys):
    """ Modify a pdb to remove the sidechains and optionally keep cysteines

    :author: Claudia Millan
    :email: cmncri@ibmb.csic.es

    :param pdb_model:
    :type pdb_model:
    :param poliA:
    :type poliA:
    :param cys:
    :type cys:
    :return:
    :rtype:
    """
    # Prepare input pdb depending on choices and write it
    pdb_file = open(pdb_model, 'r')
    pdb_lines = pdb_file.readlines()
    pdb_file.close()
    pdb_medio = open(pdb_model, 'w')  # Overwrite the contents of the previous one
    for line in pdb_lines:
        if not line.startswith("ANISO") and not line.startswith("ATOM") and not line.startswith("HETATM"):
            pdb_medio.write(line)
        elif line.startswith("ATOM") or line.startswith("HETATM"):
            parts = line.split()
            type_res = parts[3]
            if type_res.endswith('HOH'):
                continue  # go to next line
            if line.startswith("HETATM"):
                if type_res not in ['MSE','SEP','TPO','MIR']: # NOTE: should I include more non-standard residues?
                    continue # go to next line
            if poliA == False and cys == False:
                pdb_medio.write(line)  # We do not need to do any selection, just write
            elif poliA == True and cys == True:  # Then we have to save only poliA but mantain the cysteines
                list_items = list(line)
                atom = ''.join(list_items[13:16])
                type_at = atom.strip()
                if type_at in ["CA", "CB", "N", "C", "O", "SG"]:
                    pdb_medio.write(line)
            elif poliA == True and cys == False:  # Plain poliala
                list_items = list(line)
                atom = ''.join(list_items[13:16])
                type_at = atom.strip()
                if type_at in ["CA", "CB", "N", "C", "O"]:
                    pdb_medio.write(line)
            elif poliA == False and cys == True:  # This is redundant, if it has sidechains it will have its cysteins, Same as first option
                pdb_medio.write(line)
    pdb_medio.close()

def modify_chains_according_to_shredder_annotation(pdb, dictio_annotation, annotation_level, output_path):
    # TODO CM: modify to use get_pdb_from_list_of_atoms instead of the deprecated one
    """ Given a pdb or a list of pdbs, using the annotation dictionary, uses one of the annotation levels
    and produce and rewrites the pdbs with that chain definition

    :author: Claudia Millan
    :email: cmncri@ibmb.csic.es

    :param pdb: paths to the pdbs to modify
    :type pdb: str or list of str
    :param dictio_annotation: following format one key per each residue inside
           419: {'residue_object': <Residue ARG het=  resseq=419 icode= >, 'ss_type_res': 'bs', 'ori_nameres': 'ARG',
           'ori_nres': 419, 'ss_reslist': [('1hdh_0_0', 0, 'A', (' ', 419, ' ')), ('1hdh_0_0', 0, 'A', (' ', 420, ' ')),
           ('1hdh_0_0', 0, 'A', (' ', 421, ' ')), ('1hdh_0_0', 0, 'A', (' ', 420, ' ')), ('1hdh_0_0', 0, 'A', (' ', 421, ' '))]
           , 'first_ref_cycle_group': 'group0', 'third_ref_cycle_group': 'group21', 'second_ref_cycle_group': 'group0',
           'ss_id_res': 'bs36', 'ori_chain': 'A', 'ori_full_id': ('1hdh_0_0', 0, 'A', (' ', 419, ' '))}
    :type dictio_annotation: dict
    :param annotation_level: can be: 'third_ref_cycle_group','second_ref_cycle_group','first_ref_cycle_group'
    :type annotation_level: str
    :param output_path: path where the pdb(s) with the changes in the annotation must be written
    :type output_path: str
    :return:
    :rtype:
    """
    dictio_chainid = {}
    if not isinstance(pdb, list):
        pdb = [pdb]
    for i, pdb_file in enumerate(pdb):
        structure = get_structure(name=os.path.basename(pdb_file[:-4]),pdbf=pdb_file)
        for model in structure:
            for chain in model:
                for residue in chain:
                    key_chain = residue.get_full_id()  # that is the key for the dictio_chains dictionary
                    key_annotation = key_chain[3][1]
                    group = int(dictio_annotation[key_annotation][annotation_level][5:])
                    indx_group = group
                    try:
                        dictio_chainid[key_chain] = list_id[indx_group]  # the chain id must be different per each different group!
                    except:
                        print('There are too many groups defined, there are not any more possible ids')
                        sys.exit(0)
        outputpdb_path = os.path.join(output_path, os.path.basename(pdb_file))
        pdb_file_atoms = Bio.PDB.Selection.unfold_entities(structure, 'A')
        pdb_file_atoms = sorted(pdb_file_atoms, key=lambda x:x.get_parent().get_full_id()[3][1])  # sort by res number
        get_pdb_from_list_of_atoms(reference=pdb_file_atoms, path_output_pdb=outputpdb_path, dictio_chains=dictio_chainid,
                                   normalize=False, sort_reference=True, renumber=False, uniqueChain=False,
                                   polyala=False, maintainCys=False, write_pdb=True)


def get_CA_distance_matrix(pdb_model):
    """

    :param pdb_model:
    :type pdb_model:
    :return:
    :rtype:
    """
    structure = get_structure(name=pdb_model[:-4], pdbf=pdb_model)
    list_for_matrix=[]
    names_matrix_dict={}
    list_residues = Bio.PDB.Selection.unfold_entities(structure,'R')
    list_CA_atoms = [ residue['CA'] for _,residue in enumerate(list_residues)]
    for i in range(len(list_CA_atoms)):
        list_for_matrix.append([])
        for j in range(len(list_CA_atoms)):
            #print 'i,list_CA_atoms[i].get_full_id()[3][1],j,list_CA_atoms[j].get_full_id()[3][1]',i,list_CA_atoms[i].get_full_id()[3][1],j,list_CA_atoms[j].get_full_id()[3][1]
            id_first=list_CA_atoms[i].get_full_id()[3][1]
            id_second=list_CA_atoms[j].get_full_id()[3][1]
            list_for_matrix[i].append(list_CA_atoms[i]-list_CA_atoms[j])
            if names_matrix_dict.has_key(id_first):
                names_matrix_dict[id_first][id_second]=[i,j]
            else:
                names_matrix_dict[id_first]={id_second: [i,j]}
    distance_CA_matrix=numpy.array(list_for_matrix)
    numpy.set_printoptions(precision=3)
    #print '\n',distance_CA_matrix
    #print '\n', names_matrix_dict
    return distance_CA_matrix,names_matrix_dict


def shredder_spheres(working_directory, namedir, pdb_model, dictio_template, target_size, dist_matrix, convNamesMatrix,
                     min_ah=7, min_bs=4, step=1, list_centers=[]):
    """ Generates a set of compact models.

    :param working_directory: current working directory in the SHREDDER run
    :type working_directory: str
    :param namedir: output folder
    :type namedir: str
    :param pdb_model: template to extract the models from
    :type pdb_model: str
    :param dictio_template: annotation of the pdb given in pdb_model in terms of secondary and tertiary structure
    :type dictio_template: dict
    :param target_size: size that the models should have
    :type target_size: int
    :param dist_matrix:
    :type dist_matrix:
    :param convNamesMatrix:
    :type convNamesMatrix:
    :param min_ah:
    :type min_ah:
    :param min_bs:
    :type min_bs:
    :param step: step to traverse the sequence
    :type step: int
    :param list_centers: [(name_frag(str),center(list of floats with x,y,z coord of atom)),...]
                        if not empty, only the CA in the list will be used for model generation
    :type list_centers: list of tuples
    :return:
    :rtype:
    """

    # Recognize the path and create the library folder
    current_wd = working_directory
    wd_library = os.path.join(current_wd, namedir)
    if not os.path.exists(wd_library):
        os.mkdir(wd_library)
    elif os.path.exists(wd_library):
        shutil.rmtree(wd_library)
        os.mkdir(wd_library)

    # Generate input for the search
    print('######################################################################################')
    print('GENERATING MODELS FROM STARTING TEMPLATE AT ', pdb_model)
    print('######################################################################################')

    # Get the list with all CAs in the template
    structure = get_structure(name=pdb_model[:-4], pdbf=pdb_model)
    list_all_CA_atoms = [residue['CA']
                         for residue in Bio.PDB.Selection.unfold_entities(structure, 'R')
                         if residue.has_id('CA')]


    # Check the list_centers option and act accordingly
    if not list_centers:  # Then we want to use ALL the centers defined by the number of residues and step
        for i in range(0, len(list_all_CA_atoms), step):
            nfragtag = str((list_all_CA_atoms[i].get_full_id())[3][1])
            center = list_all_CA_atoms[i].get_coord()
            list_centers.append((nfragtag, center))

    log_distance_models = open('distance_models_shredder.txt', 'w')
    for i, _ in enumerate(list_centers):

        # Identify which is the residue from we will be generating the model
        name_frag = list_centers[i][0]
        print('\n \n \n \n **=====******======******======****======********===********===***********===******')
        print('\n Processing model centered in ', name_frag)

        # Obtain the list of pairwise distances between this residue and all the rest
        sorted_dist_list = get_sorted_distance_list_to_CA(dist_matrix, convNamesMatrix, name_frag)

        # Prepare the lists in which we will perform the model generation
        residues_on_list = [[sorted_dist_list[x][0], 'off'] for x, _ in enumerate(sorted_dist_list)]
        new_list_sort = [[sorted_dist_list[x][0],
                          sorted_dist_list[x][1],
                          dictio_template[sorted_dist_list[x][0]]['ss_id_res']]
                         for x, _ in enumerate(sorted_dist_list)]
        only_nres = [new_list_sort[ni][0] for ni, _ in enumerate(new_list_sort)]
        only_nres_sorted = sorted(only_nres)


        # Start the model generation
        residues_on = 0

        for ires, resi in enumerate(new_list_sort):

            if residues_on > target_size:
                print('\n We passed the target size, reducing the model')
                added.sort(key=operator.itemgetter(1))
                resremove = abs(target_size - residues_on)
                count = 0
                for ind, element in enumerate(added):
                    if count == resremove:
                        break
                    indx = only_nres.index(element[1])
                    residues_on_list[indx][1] = 'off'
                    residues_on -= 1
                    count += 1

            if residues_on == target_size:
                print('\n We reached exactly the target size')
                break

            if target_size - max(min_ah,min_bs) < residues_on <= target_size:
                print('\n We almost reached the target size')
                break

            if residues_on_list[ires][1] == 'on':  # we skip it, it was already selected
                continue
            else:
                resi_ss = resi[2]
                prev_resi_id = resi[0]
                if resi_ss.startswith('bs'):  # limit to minimal size of beta strands
                    limit_ss = min_bs
                elif resi_ss.startswith('ah'):  # limit to minimal size of alpha helices
                    limit_ss = min_ah
                elif resi_ss.startswith('coil'):  # limit to minimal size of coil
                    limit_ss = 1
                # Check what other things we can add
                added = []
                for inext in range(ires, len(new_list_sort)):
                    if len(added) >= limit_ss:
                        break
                    current_resi_id = new_list_sort[inext][0]
                    current_resi_ss = new_list_sort[inext][2]
                    if current_resi_ss == resi_ss:
                        # If the closest residue of the same ss is not on, set it
                        if residues_on_list[inext][1] == 'off':
                            added.append((inext, current_resi_id))
                            residues_on_list[inext][1] = 'on'
                            residues_on = residues_on + 1
                            # Add the remaining residues in between these two
                            current_ind = only_nres_sorted.index(current_resi_id)
                            prev_ind = only_nres_sorted.index(prev_resi_id)
                            if abs(current_ind - prev_ind) > 1:
                                mini = min(current_ind, prev_ind)
                                maxi = max(current_ind, prev_ind)
                                list_cutind = only_nres_sorted[mini + 1:maxi]
                                for ele in list_cutind:
                                    iord = only_nres.index(ele)
                                    if residues_on_list[iord][1] == 'off':
                                        residues_on_list[iord][1] = 'on'
                                        residues_on = residues_on + 1
                                        added.append((iord, ele))

                        prev_resi_id = current_resi_id


        # Write the pdb with the residues that are set to on
        to_save_nres = [ele[0] for ele in residues_on_list if ele[1] == 'on']
        structure = get_structure(name=pdb_model[:-4], pdbf=pdb_model)
        io = Bio.PDB.PDBIO()
        io.set_structure(structure)
        for model in structure.get_list():
            for chain in model.get_list():
                for residue in chain.get_list():
                    residue_nres = residue.get_full_id()[3][1]
                    if not (residue_nres in to_save_nres):
                        chain.detach_child(residue.id)
        pdbmodel_path = wd_library + "/" + 'frag' + name_frag + '_0_0.pdb'
        new_list_atoms = Bio.PDB.Selection.unfold_entities(structure, 'A')
        new_list_atoms = sorted(new_list_atoms,
                                key=lambda x: x.get_parent().get_full_id()[3][1])  # sort by residue number

        #write_pdb_file_from_list_of_atoms(new_list_atoms, pdbmodel_path, dictio_chains={}, renumber=False, uniqueChain=False)
        get_pdb_from_list_of_atoms(reference=new_list_atoms, renumber=False, polyala=False, maintainCys=False,
                                   normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={},
                                   write_pdb=True, path_output_pdb=pdbmodel_path)

        # Check the new current model size
        list_nres_elongations=[]
        list_ca = [ atom for atom in new_list_atoms if atom.id == 'CA']
        size = len(list_ca)
        print('\n     Size before elongation', size)
        diff_res = target_size - size
        if diff_res > 0:
            # Note CM: including a condition to avoid doing elongation if we are already really close to target
            if diff_res > min(min_ah,min_bs):  # we can test different values here
                print('\n     We are going to extend the secondary structure elements of the model by ',diff_res)
                dictio_template, elong_bool, list_nres_elongations  = elongate_extremities(pdb_model=pdbmodel_path, dictio_template=dictio_template,
                                                                   list_distances_full=sorted_dist_list, target_size=target_size,
                                                                   res_to_complete=diff_res, min_ah=min_ah, min_bs=min_bs)
                if elong_bool == True:  # elongation went OK, we want to keep this model
                    print('\n This model was correctly elongated, we will keep it')
                else:
                    print('============================================================================')
                    print('\n Something went wrong with the elongation of this model, we will skip it')
                    print('============================================================================')
                    os.remove(pdbmodel_path)
            else:
                print('\n     This model is really close to size required, skipping elongation')

        else:
            print('\n     This model has already the size required')


        if len(list_nres_elongations)>0:
            distances_list = [ele for ele in sorted_dist_list if (ele[0] in to_save_nres) or (ele[0] in list_nres_elongations)]
            distances_only = [ele[1] for ele in distances_list]
        else:
            distances_list = [ ele for ele in sorted_dist_list if ele[0] in to_save_nres ]
        distances_only=[ele[1] for ele in distances_list]
        log_distance_models.write(pdbmodel_path+'\t'+str(max(distances_only))+'\n')

    del log_distance_models

    # Filter the redundancy that might remain anyway
    # TODO CM: Filter using a different method
    print("\n********************************************************************************")
    print('Before filtering there are ', len(os.listdir(wd_library)), ' models')
    filter_models_by_coordinates(wd_library)
    print('After filtering there are ', len(os.listdir(wd_library)), ' models')
    print("********************************************************************************\n")

    return dictio_template


def get_sorted_distance_list_to_CA(dist_matrix,convNamesMatrix,center_name):
    """

    :param dist_matrix:
    :type dist_matrix:
    :param convNamesMatrix:
    :type convNamesMatrix:
    :param center_name:
    :type center_name:
    :return:
    :rtype:
    """
    #print ' I need to get all distances to residue ',center_name
    #print 'check where to search in the matrix, convNamesMatrix[int(center_name)]',convNamesMatrix[int(center_name)]
    list_distances=[]
    key_center=int(center_name)
    list_possible_keys=convNamesMatrix.keys()
    for _,key in enumerate(list_possible_keys):
        index_i=convNamesMatrix[key_center][key][0]
        index_j=convNamesMatrix[key_center][key][1]
        # Get the values with the correct index
        value_distance=dist_matrix[index_i][index_j]
        list_distances.append((key,value_distance))
    list_distances.sort(key = lambda x: x[1])
    #return list_distances[1:]
    return list_distances

def filter_models_by_coordinates(path_folder):
    """ Check a folder of pdbs, if they are identical in coordinates, remove the copies and leave one representative.

    :param path_folder:
    :type path_folder:
    :return:
    :rtype:
    """
    # NOTE CM: this could be improved a lot by using something faster and safer
    redundant = []
    complete_list = os.listdir(path_folder)
    dict_coord = {}
    for __index, name in enumerate(complete_list):
        structure = get_structure(name=name[:-4], pdbf=os.path.join(path_folder, name))
        dict_coord[name] = sorted([list(a.get_coord()) for a in Bio.PDB.Selection.unfold_entities(structure, 'A')],
                                  key=lambda x: (x[0], x[1], x[2]))
    # Now we can start to compare
    for i, name1 in enumerate(complete_list):
        coord1 = dict_coord[name1]
        for j, name2 in enumerate(complete_list):
            if j <= i:
                continue
            coord2 = dict_coord[name2]
            if len(coord1) != len(coord2):
                continue
            if all([coord1[k] == coord2[k] for k in range(len(coord1))]):
                redundant.append(name2)
    # print "len(redundant)",len(set(redundant))
    for __index, redundant_model in enumerate(set(redundant)):
        os.remove(os.path.join(path_folder, redundant_model))


def elongate_extremities(pdb_model, dictio_template, list_distances_full, res_to_complete, target_size, min_ah=7, min_bs=4):
    """ Extends the models generated by shredder_spheres by looking at the extremities of the fragments.

    :param pdb_model:
    :type pdb_model: str
    :param dictio_template:
    :type dictio_template:
    :param list_distances_full:
    :type list_distances_full:
    :param res_to_complete:
    :type res_to_complete:
    :param min_ah:
    :type min_ah:
    :param min_bs:
    :type min_bs:
    :return:
    :rtype:
    """

    trials_limit = 0
    list_already_elongated = []
    structure = get_structure(name=pdb_model[:-4], pdbf=pdb_model)
    list_residues = sorted(Bio.PDB.Selection.unfold_entities(structure, 'R'),
                           key=lambda x: x.get_full_id()[3][1:])  # list of residues objects sorted by id
    list_initial_nres = [resi.get_full_id()[3][1] for resi in list_residues]
    list_initial_idss = list(set([dictio_template[nres]['ss_id_res'] for nres in list_initial_nres]))

    while trials_limit < 201:  # number of times you will perform the iterative process as a maximum

        trials_limit = trials_limit + 1

        # Reread the PDB
        structure = get_structure(name=pdb_model[:-4], pdbf=pdb_model)
        list_resi_sorted = sorted(Bio.PDB.Selection.unfold_entities(structure, 'R'), key=lambda x: x.get_full_id()[3][1:])
        list_distances = []
        list_nres_elongations = []
        list_removal = []

        # Get the extremities of the continues stretches on the model
        list_extremities = []
        continuous = []
        continuous_fraglist = []
        for i, resi in enumerate(list_resi_sorted):
            if i < len(list_resi_sorted) - 1:
                check = check_continuity(res1=resi, res2=list_resi_sorted[i + 1])
                if not check:
                    list_extremities.append(('end', resi))
                    list_extremities.append(('start', list_resi_sorted[i + 1]))
                    if resi.get_full_id()[3][1] not in continuous:
                        continuous.append(resi.get_full_id()[3][1])
                    continuous_fraglist.append(continuous)
                    continuous = []
                    if i == len(list_resi_sorted) - 2:
                        continuous_fraglist.append([list_resi_sorted[i + 1].get_full_id()[3][1]])
                else:
                    if resi.get_full_id()[3][1] not in continuous:
                        continuous.append(resi.get_full_id()[3][1])
                    if list_resi_sorted[i + 1].get_full_id()[3][1] not in continuous:
                        continuous.append(list_resi_sorted[i + 1].get_full_id()[3][1])
            else:
                break
        if continuous != [] and (continuous not in continuous_fraglist):
            continuous_fraglist.append(continuous)

        # You need to add the two extremes that are so by definition, that is, the first and the last residue
        list_extremities.append(('end', list_resi_sorted[-1]))
        list_extremities.append(('start', list_resi_sorted[0]))

        continuous_fraglist.sort(key=lambda x: len(x))

        list_idsizetuple = []
        for stretch in continuous_fraglist:
            list_residues_ss = []
            for residue in stretch:
                ss_ident = dictio_template[residue]['ss_id_res']
                list_residues_ss.append((residue, ss_ident))

            list_groups = [list(group) for key, group in itertools.groupby(list_residues_ss, operator.itemgetter(1))]

            for current in list_groups:
                current_group_ss = current[0][1]  # the first one gives us the key
                list_resi = [ele[0] for ele in current]
                list_idsizetuple.append((current_group_ss, list_resi))

        list_idsizetuple.sort(key=lambda x: len(x[1]))

        if res_to_complete == 0:
            if len(list_idsizetuple[0][1]) >= min_ah and list_idsizetuple[0][0].startswith('ah'):
                break
            if len(list_idsizetuple[0][1]) >= min_bs and list_idsizetuple[0][0].startswith('bs'):
                break
            if len(list_idsizetuple[0][1]) >= 1 and list_idsizetuple[0][0].startswith('coil'):
                break
            for i in range(len(list_idsizetuple)):
                cont_section_ss = list_idsizetuple[i]
                ss_ident_section = dictio_template[cont_section_ss[1][0]]['ss_id_res']
                list_res = map(lambda x: x[-1][1], dictio_template[cont_section_ss[1][0]]['ss_reslist'])
                if ss_ident_section.startswith('ah') and len(cont_section_ss[1]) < min_ah:
                    remain = min_ah - len(cont_section_ss[1])
                elif ss_ident_section.startswith('bs') and len(cont_section_ss[1]) < min_bs:
                    remain = min_bs - len(cont_section_ss[1])
                # rest is in common
                not_yet = [val for val in list_res if val not in cont_section_ss[1]]
                for l in range(1, len(list_idsizetuple)):
                    longest_ss_id = list_idsizetuple[-l][0]
                    longest_ss_res = list_idsizetuple[-l][1]
                    if longest_ss_id == ss_ident_section:
                        continue
                    else:
                        break
                # check that longest_ss does not contain already residues we want to add
                if len(set(not_yet).intersection(set(longest_ss_res))) != 0:  # THIS SHOULD NOT HAPPEN!
                    print('There was a problem, please report to bugs-borges@ibmb.csic.es')
                    sys.exit(0)
                else:
                    list_removal.extend(longest_ss_res[-remain:])
                for index, _ in enumerate(not_yet):
                    if index == len(list_removal):
                        break
                    list_nres_elongations.append(not_yet[index])
                break
        elif res_to_complete < 0:
            print('Something very wrong happened, please report to bugs-borges@ibmb.csic.es')
            sys.exit(1)
        else:
            if trials_limit == 201:
                if res_to_complete > 10:
                    # Then I want to exclude this model
                    return dictio_template, False
                else:
                    # Then I am fine, just return OK
                    return dictio_template, True
        # Retrieve the distance from the CA defined in center to all the extremities
        for _, residue_tuple in enumerate(list_extremities):
            residue = residue_tuple[1]
            tag_ext = residue_tuple[0]
            nres = residue.get_full_id()[3][1]
            for i, _ in enumerate(list_distances_full):
                if list_distances_full[i][0] == nres:
                    list_distances.append((list_distances_full[i][1], residue.get_full_id(), tag_ext))
        list_distances.sort(key=lambda x: x[0])

        # Check that the extremes can be elongated
        for i, _ in enumerate(list_distances):
            tag_ext = list_distances[i][2]
            resi_full_id = list_distances[i][1]
            nres = (resi_full_id[3][1])
            # modify reslist to check the numerical id only
            filter_reslist = map(lambda x: x[-1], dictio_template[nres]['ss_reslist'])
            preext_ind = (filter_reslist).index(resi_full_id[-1])
            # two possibilities for extension, depending on n or cterminal
            if preext_ind == 0 and tag_ext == 'start':  # we can't extend below
                continue
            elif preext_ind == len(filter_reslist) - 1 and tag_ext == 'end':  # we can't extend after
                continue
            else:
                if tag_ext == 'end':
                    sup_add = filter_reslist[preext_ind + 1][1]
                    if (sup_add not in list_already_elongated) and (sup_add not in list_initial_nres):
                        list_nres_elongations.append(sup_add)
                elif tag_ext == 'start':
                    inf_add = filter_reslist[preext_ind - 1][1]
                    if (inf_add not in list_already_elongated) and (inf_add not in list_initial_nres):
                        list_nres_elongations.append(inf_add)

        # If there are no points for elongation we need to go to another secondary structure element
        if len(list_nres_elongations) == 0:
            if res_to_complete < min(min_ah,min_bs): # If adding a new one is going to make it incomplete
                break
            # Otherwhise search for the next ss element that I can add
            for i, _ in enumerate(list_distances_full):
                if (list_distances_full[i][0] not in list_already_elongated) and \
                        (list_distances_full[i][0] not in list_initial_nres) and \
                        (dictio_template[list_distances_full[i][0]]['ss_id_res'] not in list_initial_idss):
                    next_res = list_distances_full[i][0]
                    list_nres_elongations.extend([next_res])
                    break
                else:
                    continue

        # Remove what needs to be removed
        if len(list_removal) > 0:
            for model in structure.get_list():
                for chain in model.get_list():
                    for residue in chain.get_list():
                        nres_res = residue.get_full_id()[3][1]
                        if nres_res in list_removal:
                            try:
                                index_res = list_already_elongated.index(nres_res)
                                del (list_already_elongated[index_res])
                            except:
                                pass
                            try:
                                index_res2 = list_initial_nres.index(nres_res)
                                del (list_initial_nres[index_res2])
                            except:
                                pass
                            mini_id = residue.id
                            chain.detach_child(mini_id)
                            res_to_complete = res_to_complete + 1
            # flush list_removal
            list_removal = []

        # Perform the actual elongation of the model
        for nres in list_nres_elongations:
            addresobj = dictio_template[nres]['residue_object']
            id_chain_where_to_add = dictio_template[nres]['ori_chain']
            if (res_to_complete > 0):  # to be sure we don't add more than we need
                try:
                    structure[0][id_chain_where_to_add].add(addresobj)
                    res_to_complete = res_to_complete - 1
                    list_already_elongated.append(nres)
                except:
                    exctype, value = sys.exc_info()[:2]
                    if str(value).endswith('defined twice'):  # Then the residue is already in the structure
                        pass
                    else:
                        print('Something wrong happened with the pdb construction: ', value)

                        sys.exit(0)

        # Save the model before the next iteration
        list_atoms_sorted = sorted(Bio.PDB.Selection.unfold_entities(structure, 'A'),
                                   key=lambda x: x.get_parent().get_full_id()[3][1:])  # sort by residue number
        #         get_pdb_from_list_of_atoms(reference=new_list_atoms, renumber=False, polyala=False, maintainCys=False,
        #                           normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={},
        #                           write_pdb=True, path_output_pdb=pdbmodel_path)
        get_pdb_from_list_of_atoms(reference=list_atoms_sorted, path_output_pdb=pdb_model, write_pdb=True,
                                   renumber=False, uniqueChain=False, polyala=False, maintainCys=False,
                                   normalize=False, sort_reference=True, remove_non_res_hetatm=False, dictio_chains={})
        # Flush the list of the elongations
        list_nres_elongations = []

    return dictio_template, True, list_nres_elongations

def write_csv_node_file(g, reference,pdbsearchin, min_diff_ah, min_diff_bs):

    o = open("write_csv_node_file.log", 'w')

    ss_record = pdbsearchin.split('\n')
    ss_record_dict = {}

    def catch_substring(a, b, line):
        try:
            return line[a:b].strip()
        except:
            return ""

    for i, element in enumerate(ss_record):
        if ss_record[i] != '':
            ss_record[i]=(element.split())
            o.write(str(ss_record[i]))

            if element[0:6].strip() == 'HELIX':
                ss_record_dict[catch_substring(19, 20, element) + '_' + catch_substring(21, 25, element) + '_' + catch_substring(33, 37, element)] =\
                    {'ss': element[0:6].strip(), 'ss_position': '1', 'chain': catch_substring(19, 20, element),
                                       'res_start': catch_substring(21, 25, element), 'res_end': catch_substring(33, 37, element), 'ss_direction': '0', 'ss_id': catch_substring(7, 10, element)}
                ss_id = int(catch_substring(7, 10, element))

            elif element[0:6].strip() == 'SHEET':
                if int(catch_substring(7, 10, element)) == 1:
                    ss_id += 1
                ss_record_dict[catch_substring(21, 22, element) + '_' + catch_substring(22, 26, element) + '_' +
                               catch_substring(33, 37, element)] ={'ss': element[0:6].strip(), 'ss_position': catch_substring(7, 10, element), 'chain': catch_substring(21, 22, element),
                                       'res_start': catch_substring(22, 26, element), 'res_end': catch_substring(33, 37, element), 'ss_direction': catch_substring(38, 40, element), 'ss_id':ss_id}

            else:
                o.write("\nThis is not a conventional Helix/Sheet record")
                o.write(str(element[0:6].strip()))
        else:
            ss_record.remove(ss_record[i])

    #o.write(str(ss_record_dict))

    o.write("\n===========================================================================================================")

    f = open('csv_node_file.csv', 'w')
    f.write("identifier,pdb_id,model,chain,res_start,res_end,ah_strict,bs_strict,ss_type,ss_id,ss_position,ss_direction,sequence")
    for frag in g.vs:
        #print(frag)
        identifier = (os.path.basename(reference)[:-4]+'_' + str(frag['reslist'][0][1])+'_'+
                      str(frag['reslist'][0][2]) + '_' + str(frag['reslist'][0][3][1])+'_'+str(frag['reslist'][-1][3][1])
                      +'_'+ str(min_diff_ah) +'_'+ str(min_diff_bs))
        if frag['sstype'] == 'coil': #Si el fragmento del grafo es coil
            pass

        elif str(frag['reslist'][0][2]) + '_' + str(frag['reslist'][0][3][1])+'_'+str(frag['reslist'][-1][3][1]) not in ss_record_dict: #Hay algçun tipo de error en comparar el grafo y el diccionario
            o.write("\nThere is a dismatch in your identifiers\n")
            o.write(str(frag['reslist'][0][2]) + '_' + str(frag['reslist'][0][3][1]) + '_' + str(frag['reslist'][-1][3][1]))
            #print(frag)
            print((str(frag['reslist'][0][2])) + '_' + str(frag['reslist'][0][3][1])+'_'+str(frag['reslist'][-1][3][1]))

        elif str(frag['reslist'][0][2]) + '_' + str(frag['reslist'][0][3][1])+'_'+str(frag['reslist'][-1][3][1]) in ss_record_dict: #En el caso que se pueda comparar el fragmetno delgrafo y el diccionario
            key = str(frag['reslist'][0][2]) + '_' + str(frag['reslist'][0][3][1])+'_'+str(frag['reslist'][-1][3][1])
            #print(key)
            f.write('\n')
            f.write(identifier + ',' + os.path.basename(reference)[:-4] + ',' + str(frag['reslist'][0][1]) + ',' + str(frag['reslist'][0][2]) + ',' + str(frag['reslist'][0][3][1]) + ','
                    + str(frag['reslist'][-1][3][1]) + ',' + str(min_diff_ah) + ','+ str(min_diff_bs) + ',' + str(frag['sstype']) + ',' + str(ss_record_dict[key]['ss_id']) + ',' +
                    str(ss_record_dict[key]['ss_position']) + ',' + str(ss_record_dict[key]['ss_direction']) + ',' + str(frag['sequence']))

            o.write((identifier + ',' + os.path.basename(reference)[:-4] + ',' + str(frag['reslist'][0][1]) + ',' +
                    str(frag['reslist'][0][2]) + ',' + str(frag['reslist'][0][3][1]) + ',' +
                    str(frag['reslist'][-1][3][1]) + ',' + str(min_diff_ah) + ','+ str(min_diff_bs) +',' + str(frag['sstype']) + ',' + str(ss_record_dict[key]['ss_id']) + ',' +
                    str(ss_record_dict[key]['ss_position']) + ',' + str(ss_record_dict[key]['ss_direction'])
                    + ',' + str(frag['sequence'])))
            o.write('\n')

            ss_record_dict[frag.index]=str(identifier) #Añadir una llave con la correspondencia entre el indice del nodo y el identificador

        else: #Error no esperado
            o.write("Not expected condition")
    f.close()
    o.close()
    return(ss_record_dict)

def write_csv_edge_file (g, ss_record_dict):
    #STILL IN DEVELOPING
    f = open('csv_edge_file.csv', 'w')
    f.write("node1_id,node2_id,weight\n")

    o = open("write_csv_node_file.log", 'w')

    for frag in g.es:
        try:
            f.write(str(ss_record_dict[frag.source]) + ',' + str(ss_record_dict[frag.target]) + ',' + str(frag['weight']) + '\n')
        except:
            o.write("Somethhing happened during the edge processing")
            try:
                o.write(frag)
            except:
                print("No frag")
                
    f.close()
    o.close()

def get_atoms_list(pdb):
    """ Generate a list with the atoms from a pdb file.

    :author: Ana del Rocío Medina Bernal from Bioinformatics.py
    :email: ambcri@ibmb.csic.es
    :param pdb: path to the pdb file
    :type pdb: str
    :return list_atoms:
    :rtype list_atoms: list
    """
    f = open(pdb, "r")
    lines = f.readlines()
    f.close()
    list_atoms = []

    for line in lines:
        lispli = line.split()
        if len(lispli) > 0 and lispli[0] in ["ATOM", "HETATM"]:
            list_atoms.append(lispli)

    return list_atoms

def change_chain(pdb, chain, atom_list=["ATOM  ", "ANISOU", "HETATM", "TER   "]):
    """ Generate a pdb file with the Chain modified

    :author: Ana del Rocío Medina Bernal from Bioinformatics.py
    :email: ambcri@ibmb.csic.es
    :param pdb: path to the pdb file
    :type pdb: str
    :param chain: chain name
    :type chain: str
    :param atom_list: pdb lines to change
    :type atom_list: str
    :return out: pdb file modified
    :rtype list_atoms: str
    """

    f = open(pdb, "r")
    lines = f.readlines()
    f.close()
    out = ""
    for line in lines:
        # only look at records indicated by atom_list
        if line[0:6] not in atom_list:
            if not line.startswith("END"):
                out += line + "\n"
            continue
        # Grab only residues belonging to chain
        out += line[:21] + chain + line[22:] + "\n"
    return out


def pdb_offset(pdb, offset):
    """
    Adds an offset to the residue column of a pdb file without touching anything
    else.

    :author: Ana del Rocío Medina Bernal from Bioinformatics.py
    :email: ambcri@ibmb.csic.es
    :param pdb: path to the pdb file
    :type pdb: str
    :param offset: chain name
    :type offset: int
    :return out: pdb file modified
    :rtype list_atoms: str
    """

    # Read in the pdb file
    f = open(pdb,'r')
    lines = f.readlines()
    f.close()

    out = []
    for line in lines:
        # For and ATOM record, update residue number
        if line[0:6] == "ATOM  " or line[0:6] == "TER   ":
            num = offset + int(line[22:26])
            out.append("%s%4i%s" % (line[0:22], num, line[26:]))
        else:
            out.append(line)

    return "\n".join(out)

def get_number_of_residues (pdb):
    """
       Counts the number of residues of a pdb file

       :author: Ana del Rocío Medina Bernal from Bioinformatics.py
       :email: ambcri@ibmb.csic.es
       :param pdb: path to the pdb file
       :type pdb: str
       :return number: number of residues
       :rtype list_atoms: int
       """
    stru = get_structure("ref", pdb)
    number = 0
    for model in stru.get_list():
        for chain in model.get_list():
            for residue in chain.get_list():
                if residue.has_id("CA") and residue.has_id("C") and residue.has_id("O") and residue.has_id("N"):
                    number += 1
    return number

#TO-DO --> adaptar
def get_ideal_helices_from_lenghts(list_length, pdb, reversed=False):
    helix_list = []
    helipdb = cStringIO.StringIO(pdb)
    stru = getStructure("helix", helipdb)
    for helix_length in list_length:
        if isinstance(helix_length, list) or isinstance(helix_length, tuple):
            helix_list.append(getIdealHelicesFromLenghts(helix_length, pdb, reversed=reversed))
        else:
            cont = 0
            lips = []
            allcont = 0
            for model in stru:
                for chain in model:
                    for res in chain:
                        if reversed and allcont < 70-helix_length:
                            allcont += 1
                            continue

                        allcont += 1
                        if cont < helix_length:
                            lips += res.get_list()
                            cont += 1
                        else:
                            break
            helipdb = getPDBFromListOfAtom(lips)  #AQUIII --> adaptar función
            helix_list.append(helipdb)
    return helix_list
