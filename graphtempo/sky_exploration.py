from graphtempo import *
import pandas as pd
import itertools
import copy
import plotly.express as px
import plotly.io as pio
pio.renderers.default='svg'
import plotly.graph_objects as go
import time
import os
import gc


# SKYLINE IMPLEMENTATION

# Stability (told(inx)&tnew) (maximal)

def Stab_INX_MAX(attr_val,stc,nodes,edges,time_inv):
    c=0
    intvls = []
    for i in range(1,len(edges.columns)+1-c):
        intvls.append([list(edges.columns[:i]), list(edges.columns[i:i+1])])
        c += 1
    intvls = intvls[:-1]
    skyline = {i:[] for i in range(1, len(edges.columns))}
    dominate_counter = {}
    for left,right in intvls:
        max_length = len(left)
        while len(left) >= 1:
            #print(left)
            inx,tia_inx = Intersection_Static(nodes,edges,time_inv,left+right)
            if not inx[1].empty:
                agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc)
                if attr_val in agg_inx[1].index:
                    current_w = agg_inx[1].loc[attr_val,:][0]
                    dominate_counter[str((current_w,left,right))] = 0
                    pr = len(left)
                    #print('pr: ', pr)
                    while not skyline[pr] and pr <= max_length:
                        pr += 1
                        #print('while..., pr: ', pr)
                        if pr > max_length:
                            break
                    if pr > max_length:
                        #print(pr, '>', max_length)
                        previous_w = 0
                    else:
                        #print(pr, '<=', max_length)
                        previous_w = skyline[pr][0][0]
                    if current_w > previous_w:
                        #print(current_w, '>', previous_w)
                        if len(left) == pr:
                            dominate_counter[str((current_w,left,right))] += 1
                            for s in skyline[pr]:
                                dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                dominate_counter[str(tuple(s))] = 0
                        skyline[len(left)] = [[current_w,left,right]]
                    elif current_w == previous_w:
                        if len(left) == pr:
                            skyline.setdefault(len(left),[]).append([current_w,left,right])
                    else:
                        #print(current_w, '<=', previous_w)
                        for s in skyline[pr]:
                            dominate_counter[str(tuple(s))] += 1
                    if len(left) > 1:
                        pr2 = len(left)-1
                        while not skyline[pr2] and pr2 >= 1:
                            pr2 -= 1
                            if pr2 == 0:
                                break
                        if pr2 > 0:
                            if skyline[pr2][0][0] <= current_w:
                                dominate_counter[str((current_w,left,right))] += 1
                                for s in skyline[pr2]:
                                    dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                    dominate_counter[str(tuple(s))] = 0
                                skyline[pr2] = []
            left = left[1:]
    skyline = {i:j for i,j in skyline.items() if j}
    dominate_counter = {i:j for i,j in dominate_counter.items() \
                        if list(eval(i)) in [si for s in skyline.values() for si in s]}
    return(skyline,dominate_counter)

# Time-varying

def Stab_INX_MAX_var(attr_val,nodes,edges,time_var):
    c=0
    intvls = []
    for i in range(1,len(edges.columns)+1-c):
        intvls.append([list(edges.columns[:i]), list(edges.columns[i:i+1])])
        c += 1
    intvls = intvls[:-1]
    skyline = {i:[] for i in range(1, len(edges.columns))}
    dominate_counter = {}
    for left,right in intvls:
        max_length = len(left)
        while len(left) >= 1:
            #print(left)
            inx,tva_inx = Intersection_Variant(nodes,edges,time_var,left+right)
            if not inx[1].empty:
                agg_inx = Aggregate_Variant_Dist(inx,tva_inx,left+right)
                if attr_val in agg_inx[1].index:
                    current_w = agg_inx[1].loc[attr_val,:][0]
                    dominate_counter[str((current_w,left,right))] = 0
                    pr = len(left)
                    #print('pr: ', pr)
                    while not skyline[pr] and pr <= max_length:
                        pr += 1
                        #print('while..., pr: ', pr)
                        if pr > max_length:
                            break
                    if pr > max_length:
                        #print(pr, '>', max_length)
                        previous_w = 0
                    else:
                        #print(pr, '<=', max_length)
                        previous_w = skyline[pr][0][0]
                    if current_w > previous_w:
                        #print(current_w, '>', previous_w)
                        if len(left) == pr:
                            dominate_counter[str((current_w,left,right))] += 1
                            for s in skyline[pr]:
                                dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                dominate_counter[str(tuple(s))] = 0
                        skyline[len(left)] = [[current_w,left,right]]
                    elif current_w == previous_w:
                        if len(left) == pr:
                            skyline.setdefault(len(left),[]).append([current_w,left,right])
                    else:
                        #print(current_w, '<=', previous_w)
                        for s in skyline[pr]:
                            dominate_counter[str(tuple(s))] += 1
                    if len(left) > 1:
                        pr2 = len(left)-1
                        while not skyline[pr2] and pr2 >= 1:
                            pr2 -= 1
                            if pr2 == 0:
                                break
                        if pr2 > 0:
                            if skyline[pr2][0][0] <= current_w:
                                dominate_counter[str((current_w,left,right))] += 1
                                for s in skyline[pr2]:
                                    dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                    dominate_counter[str(tuple(s))] = 0
                                skyline[pr2] = []
            left = left[1:]
    skyline = {i:j for i,j in skyline.items() if j}
    dominate_counter = {i:j for i,j in dominate_counter.items() \
                        if list(eval(i)) in [si for s in skyline.values() for si in s]}
    return(skyline,dominate_counter)

# mix: static + time varying

def Stab_INX_MAX_mix(attr_val,stc,nodes,edges,time_invar,time_var):
    c=0
    intvls = []
    for i in range(1,len(edges.columns)+1-c):
        intvls.append([list(edges.columns[:i]), list(edges.columns[i:i+1])])
        c += 1
    intvls = intvls[:-1]
    skyline = {i:[] for i in range(1, len(edges.columns))}
    dominate_counter = {}
    for left,right in intvls:
        max_length = len(left)
        while len(left) >= 1:
            #print(left)
            inx,tia_inx,tva_inx = Intersection_Mix(nodes,edges,time_invar,time_var,left+right)
            if not inx[1].empty:
                agg_inx = Aggregate_Mix_Dist(inx,tva_inx,tia_inx,stc,left+right)
                if attr_val in agg_inx[1].index:
                    current_w = agg_inx[1].loc[attr_val,:][0]
                    dominate_counter[str((current_w,left,right))] = 0
                    pr = len(left)
                    #print('pr: ', pr)
                    while not skyline[pr] and pr <= max_length:
                        pr += 1
                        #print('while..., pr: ', pr)
                        if pr > max_length:
                            break
                    if pr > max_length:
                        #print(pr, '>', max_length)
                        previous_w = 0
                    else:
                        #print(pr, '<=', max_length)
                        previous_w = skyline[pr][0][0]
                    if current_w > previous_w:
                        #print(current_w, '>', previous_w)
                        if len(left) == pr:
                            dominate_counter[str((current_w,left,right))] += 1
                            for s in skyline[pr]:
                                dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                dominate_counter[str(tuple(s))] = 0
                        skyline[len(left)] = [[current_w,left,right]]
                    elif current_w == previous_w:
                        if len(left) == pr:
                            skyline.setdefault(len(left),[]).append([current_w,left,right])
                    else:
                        #print(current_w, '<=', previous_w)
                        for s in skyline[pr]:
                            dominate_counter[str(tuple(s))] += 1
                    if len(left) > 1:
                        pr2 = len(left)-1
                        while not skyline[pr2] and pr2 >= 1:
                            pr2 -= 1
                            if pr2 == 0:
                                break
                        if pr2 > 0:
                            if skyline[pr2][0][0] <= current_w:
                                dominate_counter[str((current_w,left,right))] += 1
                                for s in skyline[pr2]:
                                    dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                    dominate_counter[str(tuple(s))] = 0
                                skyline[pr2] = []
            left = left[1:]
    skyline = {i:j for i,j in skyline.items() if j}
    dominate_counter = {i:j for i,j in dominate_counter.items() \
                        if list(eval(i)) in [si for s in skyline.values() for si in s]}
    return(skyline,dominate_counter)

# growth (tnew - told(union)) (maximal)

def Growth_UN_MAX(attr_val,stc,nodes,edges,time_inv):
    c=0
    intvls = []
    for i in range(1,len(edges.columns)+1-c):
        intvls.append([list(edges.columns[:i]), list(edges.columns[i:i+1])])
        c += 1
    intvls = intvls[:-1]
    
    skyline = {i:[] for i in range(1, len(edges.columns))}
    dominate_counter = {}
    for left,right in intvls:
        max_length = len(left)
        while len(left) >= 1:
            diff,tia_diff = Diff_Static(nodes,edges,time_inv,right,left)
            if not diff[1].empty:
                agg_diff = Aggregate_Static_Dist(diff,tia_diff,stc)
                if attr_val in agg_diff[1].index:
                    current_w = agg_diff[1].loc[attr_val,:][0]
                    dominate_counter[str((current_w,left,right))] = 0
                    pr = len(left)
                    while not skyline[pr] and pr <= max_length:
                        pr += 1
                        if pr > max_length:
                            break
                    if pr > max_length:
                        previous_w = 0
                    else:
                        previous_w = skyline[pr][0][0]
                    if current_w > previous_w:
                        if len(left) == pr:
                            dominate_counter[str((current_w,left,right))] += 1
                            for s in skyline[pr]:
                                dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                dominate_counter[str(tuple(s))] = 0
                        skyline[len(left)] = [[current_w,left,right]]
                    elif current_w == previous_w:
                        if len(left) == pr:
                            skyline.setdefault(len(left),[]).append([current_w,left,right])
                    else:
                        for s in skyline[pr]:
                            dominate_counter[str(tuple(s))] += 1
                    if len(left) > 1:
                        pr2 = len(left)-1
                        while not skyline[pr2] and pr2 >= 1:
                            pr2 -= 1
                            if pr2 == 0:
                                break
                        if pr2 > 0:
                            if skyline[pr2][0][0] <= current_w:
                                dominate_counter[str((current_w,left,right))] += 1
                                for s in skyline[pr2]:
                                    dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                    dominate_counter[str(tuple(s))] = 0
                                skyline[pr2] = []
            left = left[1:]
    skyline = {i:j for i,j in skyline.items() if j}
    dominate_counter = {i:j for i,j in dominate_counter.items() \
                        if list(eval(i)) in [si for s in skyline.values() for si in s]}
    return(skyline,dominate_counter)


# shrinkage (told(union) - tnew) (minimal)

def Shrink_UN_MIN(attr_val,stc,nodes,edges,time_inv):
    s = [[str(i)] for i in edges.columns[:-1]]
    e = [[str(i)] for i in edges.columns[1:]]
    intvls = list(zip(s,e))
    intvls = [list(i) for i in intvls]
    
    skyline = {i:[] for i in range(1, len(edges.columns))}
    dominate_counter = {}
    for left,right in intvls:
        min_length = len(left)
        flag = True
        while flag == True:
            diff,tia_diff = Diff_Static(nodes,edges,time_inv,left,right)
            if not diff[1].empty:
                agg_diff = Aggregate_Static_Dist(diff,tia_diff,stc)
                if attr_val in agg_diff[1].index:
                    current_w = agg_diff[1].loc[attr_val,:][0]
                    dominate_counter[str((current_w,left,right))] = 0
                    pr = len(left)
                    while not skyline[pr] and pr >= min_length:
                        pr -= 1
                        if pr < min_length:
                            break
                    if pr < min_length:
                        previous_w = 0
                    else:
                        previous_w = skyline[pr][0][0]
                    if current_w > previous_w:
                        if len(left) == pr:
                            dominate_counter[str((current_w,left,right))] += 1
                            for s in skyline[pr]:
                                dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                dominate_counter[str(tuple(s))] = 0
                        skyline[len(left)] = [[current_w,left,right]]
                    elif current_w == previous_w:
                        if len(left) == pr:
                            skyline.setdefault(len(left),[]).append([current_w,left,right])
                    else:
                        for s in skyline[pr]:
                            dominate_counter[str(tuple(s))] += 1
                    if left[0] != edges.columns[0]:
                        pr2 = len(left)+1
                        while not skyline[pr2] and pr2 <= len(list(edges.columns)[:list(edges.columns).index(right[0])]):
                            pr2 += 1
                            if pr2 == len(list(edges.columns)[:list(edges.columns).index(right[0])])+1:
                                break
                        if pr2 < len(list(edges.columns)[:list(edges.columns).index(right[0])])+1:
                            if skyline[pr2][0][0] <= current_w:
                                dominate_counter[str((current_w,left,right))] += 1
                                for s in skyline[pr2]:
                                    dominate_counter[str((current_w,left,right))] += dominate_counter[str(tuple(s))]
                                    dominate_counter[str(tuple(s))] = 0
                                skyline[pr2] = []
            if left[0] != edges.columns[0]:
                flag = True
                left = [edges.columns[list(edges.columns).index(left[0])-1]]+left
            else:
                flag = False
    skyline = {i:j for i,j in skyline.items() if j}
    dominate_counter = {i:j for i,j in dominate_counter.items() \
                        if list(eval(i)) in [si for s in skyline.values() for si in s]}
    return(skyline,dominate_counter)
