import pandas as pd
import numpy as np
import networkx as nx

attrs = pd.read_csv('metadata_class_gender.txt', sep='\t', index_col=0, header=None)

edges_original = pd.read_csv('primaryschool.csv', sep='\t', index_col=0, usecols=[0,1,2], header=None)

edges_idx = edges_original.index.to_numpy()
edges_idx_uniq = np.unique(edges_idx)

limit = 180 # 1 hour
uniq_time_split = []
for i in range(limit,len(edges_idx_uniq),limit):
    tmp = list(edges_idx_uniq[i-limit:i])
    uniq_time_split.append(tmp)

uniq_time_split_dict = {i:set(uniq_time_split[i]) for i in range(len(uniq_time_split))}

idx_set = set([i for lst in uniq_time_split for i in lst])
idx_to_keep_df = [j for j in edges_idx if j in idx_set]

edges = edges_original[edges_original.index.isin(idx_to_keep_df)]


edges_idx_new = []
for i in idx_to_keep_df:
    for key,val in uniq_time_split_dict.items():
        if i in val:
            edges_idx_new.append(key)

edges.index = edges_idx_new


G = nx.DiGraph()
G.add_edges_from(edges.values.tolist())
print(nx.is_weakly_connected(G))

#create list of dfs with multiindexes
lst = []
for i in range(len(uniq_time_split)):
    tmp_set = set(tuple(row) for row in edges.loc[i,:].values.tolist())
    tmp_idx = pd.MultiIndex.from_tuples(list(tmp_set))
    lst.append(pd.DataFrame([1]*len(tmp_idx), index=tmp_idx))

df_idx = []
for df in lst:
    df_idx.extend(df.index.tolist())
    
df_idx = list(set(df_idx))
df = pd.DataFrame(index = pd.MultiIndex.from_tuples(df_idx))
df = df.sort_index()

my_edges = pd.concat(lst[:], axis=1)
my_edges = my_edges.fillna(0)
my_edges = my_edges.astype(int)
my_edges.columns = [str(i+1) for i in range(len(my_edges.columns))]
my_edges.index.names = ['Left','Right']

#nodes
lst_nodes = []
for i in lst:
    idx_flat = list(set([j for tpl in i.index.tolist() for j in tpl]))
    lst_nodes.append(idx_flat)

df_idx_nodes = list(set([i for lst in df_idx for i in lst]))
df_nodes = pd.DataFrame(index = df_idx_nodes)
df_nodes = df_nodes.sort_index()
#df_nodes.columns = [str(i) for i in range(len(lst_nodes))]
for i in range(len(lst_nodes)):
    for idx in df_nodes.index.tolist():
        if idx in lst_nodes[i]:
            df_nodes.loc[idx,str(i+1)] = 1
        else:
            df_nodes.loc[idx,str(i+1)] = 0
df_nodes = df_nodes.astype(int)
df_nodes.index.name = 'userID'

my_edges.to_csv('edges.csv', sep=' ', index=True)
df_nodes.to_csv('nodes.csv', sep=' ', index=True)
attrs = pd.concat([attrs.iloc[:,1],attrs.iloc[:,0]],axis=1)
attrs.columns = ['gender', 'class']
attrs['class'] = attrs['class'].replace('Teachers','Teacher')
attrs.to_csv('time_invariant_attr.csv', sep=' ', index=True)