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


# =============================================================================
# # primary school dataset
# edges_df = pd.read_csv('../datasets/school_dataset/edges.csv', sep=' ', index_col=[0,1])
# nodes_df = pd.read_csv('../datasets/school_dataset/nodes.csv', sep=' ', index_col=0)
# time_invariant_attr = pd.read_csv('../datasets/school_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
# nodes_df.index.names = ['userID']
# interval = [i for i in edges_df.columns]
# =============================================================================


# SKYLINE IMPLEMENTATION

# Stability (told(inx)&tnew) (maximal) - DISTINCT
# Static

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



# growth (tnew - told(union)) (maximal) - DISTINCT
# static

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

# time varying

def Growth_UN_MAX_var(attr_val,nodes,edges,time_var):
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
            diff,tva_diff = Diff_Variant(nodes,edges,time_var,right,left)
            if not diff[1].empty:
                agg_diff = Aggregate_Variant_Dist(diff,tva_diff,right)
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

# mix: static + time varying

def Growth_UN_MAX_mix(attr_val,stc,nodes,edges,time_invar,time_var):
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
            diff,tia_diff,tva_diff = Diff_Mix(nodes,edges,time_invar,time_var,right,left)
            if not diff[1].empty:
                agg_diff = Aggregate_Mix_Dist(diff,tva_diff,tia_diff,stc,right)
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


# shrinkage (told(union) - tnew) (minimal) - DISTINCT

#static

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

#time varying

def Shrink_UN_MIN_var(attr_val,nodes,edges,time_var):
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
            diff,tva_diff = Diff_Variant(nodes,edges,time_var,left,right)
            if not diff[1].empty:
                agg_diff = Aggregate_Variant_Dist(diff,tva_diff,left)
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

#mix: static + time varying

def Shrink_UN_MIN_mix(attr_val,stc,nodes,edges,time_inv,time_var):
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
            diff,tia_diff,tva_diff = Diff_Mix(nodes,edges,time_inv,time_var,left,right)
            if not diff[1].empty:
                agg_diff = Aggregate_Mix_Dist(diff,tva_diff,tia_diff,stc,left)
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





# =============================================================================
# attr_values = ('M', 'M')
# stc_attrs = ['gender']
# 
# result_sky, dominance_stab = Stab_INX_MAX(attr_values,stc_attrs,nodes_df,edges_df,time_invariant_attr)
# 
# # plot
# import matplotlib.pyplot as plt
# from matplotlib import style
# import ast
# 
# 
# values_sorted = sorted(v for v in dominance_stab.values())[::-1]
# topk = values_sorted[2] # TOP-3
# dominance_stab_top = [list(ast.literal_eval(k)) for k,v in dominance_stab.items() if v >= topk]
# skyline = {k:v for k,v in result_sky.items() if v[0] in dominance_stab_top}
# colors = ['blue' if lst in dominance_stab_top else 'red' for k,v in result_sky.items() for lst in v]
# 
# 
# tps = [i for i in edges_df.columns]
# tps_int = [i for i in range(1,len(tps)+1)]
# tps_map = dict(zip(tps, tps_int))
# 
# 
# x3 = []
# y3 = []
# z3 = []
# dx = []
# dy = []
# dz = []
# for k,v in result_sky.items():
#     for lst in v:
#         x3.append(tps_map[lst[1][0]] - 0.5)
#         y3.append(tps_map[lst[-1][0]] - 0.5)
#         z3.append(0)
#         dx.append(len(lst[1]))
#         dy.append(1)
#         dz.append(lst[0])
# 
# 
# style.use('ggplot')
# fig = plt.figure(figsize=(9,9))
# ax1 = fig.add_subplot(111, projection='3d')
# 
# ax1.bar3d(x3, y3, z3, dx, dy, dz, alpha=0.2, color = colors)
# 
# pos = [i+10 for i in dz]
# for x,y,d,p in zip(x3,y3,dz,pos):
#     ax1.text(x, y, p, d, fontsize=8, horizontalalignment='left', verticalalignment='bottom', weight= 'bold')
# 
# tick_vars = [tps_map[str(i)] for i in range(1,len(tps)+1,2)]
# tick_lbl_vars = [str(tps_map[str(i)]) for i in range(1,len(tps)+1,2)]
# ax1.set_xticks(tick_vars)
# ax1.set_yticks(tick_vars)
# ax1.set_xticklabels(tick_lbl_vars, fontsize=8, rotation=10)
# ax1.set_yticklabels(tick_lbl_vars, fontsize=8, va='bottom', ha='left', rotation=-15)
# ax1.axes.get_zaxis().set_ticks([])
# 
# ax1.set_xlabel('Interval', fontsize=10)
# ax1.set_ylabel('Reference point', fontsize=10)
# #ax1.set_zlabel('count', fontsize=8)
# #ax1.view_init(None, None)
# ax1.view_init(20, -110)
# plt.show()
# =============================================================================
