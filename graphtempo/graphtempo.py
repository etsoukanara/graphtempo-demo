
#import ray
#import modin.pandas as pd
import pandas as pd
import copy
import numpy as np
import sys


######## UNION STATIC
def Union_Static(nodesdf,edgesdf,tia,intvl):
    # get union of nodes and edges on interval
    nodes_u = nodesdf[intvl][nodesdf[intvl].any(axis=1)]
    edges_u = edgesdf[intvl][edgesdf[intvl].any(axis=1)]
    tia_u = tia[tia.index.isin(nodes_u.index)]
    un = [nodes_u,edges_u]
    return(un,tia_u)

######## UNION VARIANT
def Union_Variant(nodesdf,edgesdf,tva,intvl):
    # get union of nodes and edges on interval
    nodes_u = nodesdf[intvl][nodesdf[intvl].any(axis=1)]
    edges_u = edgesdf[intvl][edgesdf[intvl].any(axis=1)]
    tva_u = tva[intvl][tva[intvl].index.isin(nodes_u.index)]
    un = [nodes_u,edges_u]
    return(un,tva_u)

######## UNION STATIC-VARIANT
def Union_Mix(nodesdf,edgesdf,tia,tva,intvl):
    # get union of nodes and edges on interval
    nodes_u = nodesdf[intvl][nodesdf[intvl].any(axis=1)]
    edges_u = edgesdf[intvl][edgesdf[intvl].any(axis=1)]
    tia_u = tia[tia.index.isin(nodes_u.index)]
    tva_u = tva[intvl][tva[intvl].index.isin(nodes_u.index)]
    un = [nodes_u,edges_u]
    return(un,tia_u,tva_u)

######## INTERSECTION STATIC
def Intersection_Static(nodesdf,edgesdf,tia,intvl):
    # get intersection of nodes and edges on interval
    nodes_inx = nodesdf[intvl][nodesdf[intvl].all(axis=1)]
    edges_inx = edgesdf[intvl][edgesdf[intvl].all(axis=1)]
    tia_inx = tia[tia.index.isin(nodes_inx.index)]
    inx = [nodes_inx,edges_inx]
    return(inx,tia_inx)

######## INTERSECTION VARIANT
def Intersection_Variant(nodesdf,edgesdf,tva,intvl):
    # get union of nodes and edges on interval
    nodes_inx = nodesdf[intvl][nodesdf[intvl].all(axis=1)]
    edges_inx = edgesdf[intvl][edgesdf[intvl].all(axis=1)]
    tva_inx = tva[intvl][tva[intvl].index.isin(nodes_inx.index)]
    inx = [nodes_inx,edges_inx]
    return(inx,tva_inx)

######## INTERSECTION STATIC-VARIANT
def Intersection_Mix(nodesdf,edgesdf,tia,tva,intvl):
    # get union of nodes and edges on interval
    nodes_inx = nodesdf[intvl][nodesdf[intvl].all(axis=1)]
    edges_inx = edgesdf[intvl][edgesdf[intvl].all(axis=1)]
    tia_inx = tia[tia.index.isin(nodes_inx.index)]
    tva_inx = tva[intvl][tva[intvl].index.isin(nodes_inx.index)]
    inx = [nodes_inx,edges_inx]
    return(inx,tia_inx,tva_inx)

######## DIFFERENCE STATIC
def Diff_Static(nodesdf,edgesdf,tia,intvl_fst,intvl_scd):
    un_init, tia_init = Union_Static(nodesdf,edgesdf,tia,intvl_fst)
    un_to_rm, tia_to_rm = Union_Static(nodesdf,edgesdf,tia,intvl_scd)
    nodes = un_init[0][~un_init[0].index.isin(un_to_rm[0].index)]
    edges = un_init[1][~un_init[1].index.isin(un_to_rm[1].index)]
    ediff_idx = set([item for i in edges.index.values.tolist() for item in i])
    tia_d = tia_init[tia_init.index.isin(ediff_idx)]
    diff = [nodes,edges]
    return(diff,tia_d)

def Diff_Variant(nodesdf,edgesdf,tva,intvl_fst,intvl_scd):
    un_init, tva_init = Union_Variant(nodesdf,edgesdf,tva,intvl_fst)
    un_to_rm, tva_to_rm = Union_Variant(nodesdf,edgesdf,tva,intvl_scd)
    nodes = un_init[0][~un_init[0].index.isin(un_to_rm[0].index)]
    edges = un_init[1][~un_init[1].index.isin(un_to_rm[1].index)]
    ediff_idx = set([item for i in edges.index.values.tolist() for item in i])
    tva_d = tva_init[tva_init.index.isin(ediff_idx)]
    diff = [nodes,edges]
    return(diff,tva_d)

def Diff_Mix(nodesdf,edgesdf,tia,tva,intvl_fst,intvl_scd):
    un_init, tia_init, tva_init = Union_Mix(nodesdf,edgesdf,tia,tva,intvl_fst)
    un_to_rm, tia_to_rm, tva_to_rm = Union_Mix(nodesdf,edgesdf,tia,tva,intvl_scd)
    nodes = un_init[0][~un_init[0].index.isin(un_to_rm[0].index)]
    edges = un_init[1][~un_init[1].index.isin(un_to_rm[1].index)]
    ediff_idx = set([item for i in edges.index.values.tolist() for item in i])
    tia_d = tia_init[tia_init.index.isin(ediff_idx)]
    tva_d = tva_init[tva_init.index.isin(ediff_idx)]
    diff = [nodes,edges]
    return(diff,tia_d,tva_d)

def Diff_Post_Agg_Static(agg,stc_attrs):
    n_df = agg[0]
    e_df = agg[1]
    e_dfnew = e_df.reset_index().drop('count', axis=1)
    eL_df = e_dfnew.iloc[:,:len(stc_attrs)]
    eR_df = e_dfnew.iloc[:,len(stc_attrs):]    
    eLR_df = pd.DataFrame(eL_df.values.tolist() + eR_df.values.tolist()).drop_duplicates()
    eLR_df = eLR_df.set_index(eLR_df.columns.values.tolist())
    n_df = pd.concat([n_df, eLR_df], axis=1).fillna(0)
    diff_agg = [n_df,e_df]
    return(diff_agg)

def Diff_Post_Agg_Variant(agg):
    n_df = agg[0]
    e_df = agg[1]
    e_dfnew = e_df.reset_index().drop('count', axis=1)
    eL_df = e_dfnew.iloc[:,0]
    eR_df = e_dfnew.iloc[:,1]    
    eLR_df = pd.DataFrame(eL_df.values.tolist() + eR_df.values.tolist()).drop_duplicates()
    eLR_df = eLR_df.set_index(eLR_df.columns.values.tolist())
    n_df = pd.concat([n_df, eLR_df], axis=1).fillna(0)
    diff_agg = [n_df,e_df]
    return(diff_agg)

def Diff_Post_Agg_Mix(agg,stc_attrs):
    n_df = agg[0]
    e_df = agg[1]
    e_dfnew = e_df.reset_index().drop('count', axis=1)
    eL_df = e_dfnew.iloc[:,:len(stc_attrs)+1]
    eR_df = e_dfnew.iloc[:,len(stc_attrs)+1:]    
    eLR_df = pd.DataFrame(eL_df.values.tolist() + eR_df.values.tolist()).drop_duplicates()
    eLR_df = eLR_df.set_index(eLR_df.columns.values.tolist())
    n_df = pd.concat([n_df, eLR_df], axis=1).fillna(0)
    diff_agg = [n_df,e_df]
    return(diff_agg)

################ AGGREGATION
def Aggregate_Static_All(oper_output,tia,stc_attrs):
    # nodes
    nodes = pd.DataFrame(oper_output[0].sum(axis=1), columns=['count'])
    for attr in stc_attrs:
        nodes[attr] = tia.loc[nodes.index,attr].values
    nodes = nodes.set_index(nodes.columns.values[1:].tolist())
    nodes = nodes.groupby(nodes.index.names).sum()
    # edges
    edges = pd.DataFrame(oper_output[1].sum(axis=1), columns=['count'])
    for attr in stc_attrs:
        edges[attr+'L'] = \
            tia.loc[edges.index.get_level_values('Left'),attr].values
    for attr in stc_attrs:
        edges[attr+'R'] = \
        tia.loc[edges.index.get_level_values('Right'),attr].values
    edges = edges.set_index(edges.columns.values[1:].tolist())
    edges = edges.groupby(edges.index.names).sum()
    
    edges_inx_names = edges.index.names
    edges_idx = edges.index.tolist()
    edges_idx_new = []
    for tpl in edges_idx:
        edges_idx_new.append(tuple([tpl[:int(len(tpl)/2)], tpl[int(len(tpl)/2):]]))
    edges_idx_new = [tuple(sorted(tuple([i[0],i[1]]))) for i in edges_idx_new]
    edges_idx_new = [tuple(tpl[0]+tpl[1]) for tpl in edges_idx_new]
    edges_idx_new = pd.MultiIndex.from_tuples(edges_idx_new)
    edges.index = edges_idx_new
    edges = edges.groupby(edges.index).sum()
    edges.index = pd.MultiIndex.from_tuples(edges.index.tolist())
    edges.index.names = edges_inx_names
    
    agg = [nodes, edges]
    return(agg)

def Aggregate_Static_Dist(oper_output,tia,stc_attrs):
    # nodes
    nodes = tia[stc_attrs].set_index(tia[stc_attrs].columns.values.tolist())
    # if oper_output[0].index.equals(tia.index):
    #     nodes = tia[stc_attrs].set_index(tia[stc_attrs].columns.values.tolist())
    # else:#difference output produces different indexes for nodes and attributes
    #     nodes = pd.DataFrame(index=oper_output[0].index)
    #     for attr in stc_attrs:
    #         nodes[attr] = tia.loc[nodes.index,attr].values
    #     nodes = nodes.set_index(nodes.columns.values.tolist())
    nodes = nodes.groupby(nodes.index.names).size().to_frame('count')
    # edges
    edges = pd.DataFrame(index=oper_output[1].index)
    for attr in stc_attrs:
        edges[attr+'L'] = \
        tia.loc[edges.index.get_level_values('Left'),attr].values
    for attr in stc_attrs:
        edges[attr+'R'] = \
        tia.loc[edges.index.get_level_values('Right'),attr].values
    edges = edges.set_index(edges.columns.values.tolist())
    edges = edges.groupby(edges.index.names).size().to_frame('count')
    
    edges_inx_names = edges.index.names
    edges_idx = edges.index.tolist()
    edges_idx_new = []
    for tpl in edges_idx:
        edges_idx_new.append(tuple([tpl[:int(len(tpl)/2)], tpl[int(len(tpl)/2):]]))
    edges_idx_new = [tuple(sorted(tuple([i[0],i[1]]))) for i in edges_idx_new]
    edges_idx_new = [tuple(tpl[0]+tpl[1]) for tpl in edges_idx_new]
    edges_idx_new = pd.MultiIndex.from_tuples(edges_idx_new)
    edges.index = edges_idx_new
    edges = edges.groupby(edges.index).sum()
    edges.index = pd.MultiIndex.from_tuples(edges.index.tolist())
    edges.index.names = edges_inx_names
    
    agg = [nodes, edges]
    return(agg)

def Aggregate_Variant_All(oper_output,tva,intvl):
    tva = tva.where(tva != 0).stack().to_frame('varying').rename_axis(['userID','time'])
    # nodes
    nodes = oper_output[0].copy()
    nodes = nodes.where(nodes != 0).stack().to_frame('varying').rename_axis(['userID','time'])
    if nodes.index.equals(tva.index):
        nodes = tva.copy()
    else:
        nodes = nodes.drop('varying', axis=1)
        nodes = nodes.join(tva)
    nodes = pd.DataFrame(index=nodes.varying)
    nodes = nodes.groupby(nodes.index.names).size().to_frame('count')
    # edges
    edges = oper_output[1].copy()
    edges = edges.where(edges != 0).stack().to_frame('varying').rename_axis(['Left','Right','time'])
    idx = edges.index
    edgesL = edges.drop('varying', axis=1).droplevel('Right').rename_axis(['userID','time'])
    #for attr in var_attrs:
    edgesL = edgesL.join(tva)
    edgesL.reset_index(inplace=True, drop=True)
    edgesR = edges.drop('varying', axis=1).droplevel('Left').rename_axis(['userID','time'])
    #for attr in var_attrs:
    edgesR = edgesR.join(tva)
    edgesR.reset_index(inplace=True, drop=True)
    #edges = pd.concat([edgesL, edgesR], axis=1)
    edgesL['varyingR'] = edgesR['varying'].values
    edgesL.index = idx
    edgesL.columns = ['varyingL','varyingR']
    edgesL = pd.DataFrame(index=[edgesL.varyingL, edgesL.varyingR])
    edgesL = edgesL.groupby(edgesL.index.names).size().to_frame('count')

    edges_inx_names = edges.index.names
    edges_idx = edges.index.tolist()
    edges_idx_new = []
    for tpl in edges_idx:
        edges_idx_new.append(tuple([tpl[:int(len(tpl)/2)], tpl[int(len(tpl)/2):]]))
    edges_idx_new = [tuple(sorted(tuple([i[0],i[1]]))) for i in edges_idx_new]
    edges_idx_new = [tuple(tpl[0]+tpl[1]) for tpl in edges_idx_new]
    edges_idx_new = pd.MultiIndex.from_tuples(edges_idx_new)
    edges.index = edges_idx_new
    edges = edges.groupby(edges.index).sum()
    edges.index = pd.MultiIndex.from_tuples(edges.index.tolist())
    edges.index.names = edges_inx_names

    agg = [nodes, edgesL]
    return(agg)

def Aggregate_Variant_Dist(oper_output,tva,intvl):
    tva = tva.where(tva != 0).stack().to_frame('varying').rename_axis(['userID','time'])
    # nodes
    nodes = oper_output[0].copy()
    nodes = nodes.where(nodes != 0).stack().to_frame('varying').rename_axis(['userID','time'])
    if nodes.index.equals(tva.index):
        nodes = tva.copy()
    else:
        nodes = nodes.drop('varying', axis=1)
        nodes = nodes.join(tva)
    # distinct
    nodes = nodes.droplevel('time')
    nodes = nodes.reset_index()
    nodes = nodes.drop_duplicates()#
    nodes = pd.DataFrame(index=nodes.varying)
    nodes = nodes.groupby(nodes.index.names).size().to_frame('count')
    # edges
    edges = oper_output[1].copy()
    edges = edges.where(edges != 0).stack().to_frame('varying').rename_axis(['Left','Right','time'])
    idx = edges.index
    edgesL = edges.drop('varying', axis=1).droplevel('Right').rename_axis(['userID','time'])
    #for attr in var_attrs:
    edgesL = edgesL.join(tva)
    edgesL.reset_index(inplace=True, drop=True)
    edgesR = edges.drop('varying', axis=1).droplevel('Left').rename_axis(['userID','time'])
    #for attr in var_attrs:
    edgesR = edgesR.join(tva)
    edgesR.reset_index(inplace=True, drop=True)
    #edges = pd.concat([edgesL, edgesR], axis=1)
    edgesL['varyingR'] = edgesR['varying'].values
    edgesL.index = idx
    edgesL.columns = ['varyingL','varyingR']
    # distinct
    edgesL = edgesL.droplevel('time')
    edgesL = edgesL.reset_index()
    edgesL = edgesL.drop_duplicates()
    #
    edgesL = pd.DataFrame(index=[edgesL.varyingL, edgesL.varyingR])
    edgesL = edgesL.groupby(edgesL.index.names).size().to_frame('count')

    edges_inx_names = edges.index.names
    edges_idx = edges.index.tolist()
    edges_idx_new = []
    for tpl in edges_idx:
        edges_idx_new.append(tuple([tpl[:int(len(tpl)/2)], tpl[int(len(tpl)/2):]]))
    edges_idx_new = [tuple(sorted(tuple([i[0],i[1]]))) for i in edges_idx_new]
    edges_idx_new = [tuple(tpl[0]+tpl[1]) for tpl in edges_idx_new]
    edges_idx_new = pd.MultiIndex.from_tuples(edges_idx_new)
    edges.index = edges_idx_new
    edges = edges.groupby(edges.index).sum()
    edges.index = pd.MultiIndex.from_tuples(edges.index.tolist())
    edges.index.names = edges_inx_names

    agg = [nodes, edgesL]
    return(agg)

def Aggregate_Mix_All(oper_output,tva,tia,stc_attrs,intvl):
    # nodes
    nodes = pd.melt(tva, value_name='variant', ignore_index=False).drop('variable', axis=1)
    # if oper_output[0].index.equals(tva.index):
    #     nodes = pd.melt(tva, value_name='variant', ignore_index=False).drop('variable', axis=1)
    # else:
    #     nodes = pd.DataFrame(index=oper_output[0].index)
    #     for i in intvl:
    #         nodes[i] = tva.loc[nodes.index,i].values
    #     nodes = pd.melt(nodes, value_name='variant', ignore_index=False).drop('variable', axis=1)
    nodes = nodes[nodes.variant!=0]
    for attr in stc_attrs:
        nodes[attr] = tia.loc[nodes.index,attr].values
    nodes = nodes.set_index(nodes.columns.values.tolist())
    nodes = nodes.groupby(nodes.index.names).size().to_frame('count')
    # edges
    edges = pd.DataFrame(index=oper_output[1].index)
    for i in intvl:
        edges[i+'L'] = tva.loc[edges.index.get_level_values('Left'),i].values
        edges[i+'R'] = tva.loc[edges.index.get_level_values('Right'),i].values
    colnames = edges.columns.values.tolist()
    lefts = [colnames[i] for i in range(0,len(colnames),2)]
    rights = [colnames[i] for i in range(1,len(colnames),2)]
    edges_lefts = edges[lefts]
    edges_rights = edges[rights]
    edges_lefts = pd.melt(edges_lefts, value_name='variantL', ignore_index=False).drop('variable', axis=1)
    edges_rights = pd.melt(edges_rights, value_name='variantR', ignore_index=False).drop('variable', axis=1)
    edgelr = pd.concat([edges_lefts,edges_rights], axis=1)
    edges = edgelr.loc[~(edgelr==0).any(axis=1)]
    for attr in stc_attrs:
        colslen = len(edges.columns)
        edges.insert(loc=colslen-1, column=attr+'L', \
            value=tia.loc[edges.index.get_level_values('Left'),attr].values)
    for attr in stc_attrs:
        colslen = len(edges.columns)
        edges.insert(loc=colslen, column=attr+'R', \
            value=tia.loc[edges.index.get_level_values('Right'),attr].values)
    edges = edges.set_index(edges.columns.values.tolist())
    edges = edges.groupby(edges.index.names).size().to_frame('count')
    
    edges_inx_names = edges.index.names
    edges_idx = edges.index.tolist()
    edges_idx_new = []
    for tpl in edges_idx:
        edges_idx_new.append(tuple([tpl[:int(len(tpl)/2)], tpl[int(len(tpl)/2):]]))
    edges_idx_new = [tuple(sorted(tuple([i[0],i[1]]))) for i in edges_idx_new]
    edges_idx_new = [tuple(tpl[0]+tpl[1]) for tpl in edges_idx_new]
    edges_idx_new = pd.MultiIndex.from_tuples(edges_idx_new)
    edges.index = edges_idx_new
    edges = edges.groupby(edges.index).sum()
    edges.index = pd.MultiIndex.from_tuples(edges.index.tolist())
    edges.index.names = edges_inx_names
    
    agg = [nodes, edges]
    return(agg)

def Aggregate_Mix_Dist(oper_output,tva,tia,stc_attrs,intvl):
    # nodes
    nodes = pd.melt(tva, value_name='variant', ignore_index=False).drop('variable', axis=1)
    # if oper_output[0].index.equals(tva.index):
    #     nodes = pd.melt(tva, value_name='variant', ignore_index=False).drop('variable', axis=1)
    # else:
    #     nodes = pd.DataFrame(index=oper_output[0].index)
    #     for i in intvl:
    #         nodes[i] = tva.loc[nodes.index,i].values
    #     nodes = pd.melt(nodes, value_name='variant', ignore_index=False).drop('variable', axis=1)
    nodes = nodes[nodes.variant!=0]
    nodes = nodes.reset_index()
    nodes.columns = ['userID', 'variant']
    nodes = nodes.drop_duplicates()
    nodes = nodes.set_index('userID')
    for attr in stc_attrs:
        nodes[attr] = tia.loc[nodes.index,attr].values
    nodes = nodes.set_index(nodes.columns.values.tolist())
    nodes = nodes.groupby(nodes.index.names).size().to_frame('count')
    # edges
    edges = pd.DataFrame(index=oper_output[1].index)
    for i in intvl:
        edges[i+'L'] = tva.loc[edges.index.get_level_values('Left'),i].values
        edges[i+'R'] = tva.loc[edges.index.get_level_values('Right'),i].values
    colnames = edges.columns.values.tolist()
    lefts = [colnames[i] for i in range(0,len(colnames),2)]
    rights = [colnames[i] for i in range(1,len(colnames),2)]
    edges_lefts = edges[lefts]
    edges_rights = edges[rights]
    edges_lefts = pd.melt(edges_lefts, value_name='variantL', ignore_index=False).drop('variable', axis=1)
    edges_rights = pd.melt(edges_rights, value_name='variantR', ignore_index=False).drop('variable', axis=1)
    edgelr = pd.concat([edges_lefts,edges_rights], axis=1)
    edges = edgelr.loc[~(edgelr==0).any(axis=1)]
    for attr in stc_attrs:
        colslen = len(edges.columns)
        edges.insert(loc=colslen-1, column=attr+'L', \
            value=tia.loc[edges.index.get_level_values('Left'),attr].values)
    for attr in stc_attrs:
        colslen = len(edges.columns)
        edges.insert(loc=colslen, column=attr+'R', \
            value=tia.loc[edges.index.get_level_values('Right'),attr].values)
    edges = edges.reset_index()
    edges = edges.drop_duplicates()
    edges = edges.drop(['Left', 'Right'], axis=1)
    edges = edges.set_index(edges.columns.values.tolist())
    edges = edges.groupby(edges.index.names).size().to_frame('count')
    
    edges_inx_names = edges.index.names
    edges_idx = edges.index.tolist()
    edges_idx_new = []
    for tpl in edges_idx:
        edges_idx_new.append(tuple([tpl[:int(len(tpl)/2)], tpl[int(len(tpl)/2):]]))
    edges_idx_new = [tuple(sorted(tuple([i[0],i[1]]))) for i in edges_idx_new]
    edges_idx_new = [tuple(tpl[0]+tpl[1]) for tpl in edges_idx_new]
    edges_idx_new = pd.MultiIndex.from_tuples(edges_idx_new)
    edges.index = edges_idx_new
    edges = edges.groupby(edges.index).sum()
    edges.index = pd.MultiIndex.from_tuples(edges.index.tolist())
    edges.index.names = edges_inx_names
    
    agg = [nodes, edges]
    return(agg)

# EFFICIENT Union
def Union_Eff(agg_tp,intvl_un):
    nagg = pd.concat([agg_tp[i][0][0] for i in intvl_un],axis=1).sum(axis=1)
    eagg = pd.concat([agg_tp[i][0][1] for i in intvl_un],axis=1).sum(axis=1)
    agg = [nagg,eagg]
    return(agg)

# EFFICIENT DIMS | give dimension(s) as subset of the standard aggregation used
def Dims_Eff(dims,agg_std):
    edims = [d+i for i in ['L', 'R'] for d in dims]
    nagg = agg_std[0].groupby(level=dims).sum()
    eagg = agg_std[1].groupby(level=edims).sum()
    agg = [nagg,eagg]
    return(agg)


    