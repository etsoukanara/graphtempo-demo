from graphtempo import *


# Stability | Inx Semantics
# a Old(INX)&New
def Stability_Intersection_a(k,intvl,nodes_df,edges_df,invar,varying,attrtype,stc_attrs,values):
    intvl_rv = intvl[::-1]
    stabI_invl_a = []
    for i in intvl[:-1]:
        stabI_invl_a.append([[i],[intvl[intvl.index(i)+1]]])  
    stabI_a = []
    if attrtype == 'Static':
        for i in stabI_invl_a:
            inx,tia_inx = Intersection_Static(nodes_df,edges_df,invar,i[0]+i[1])
            if inx[1].empty:
                continue
            else:
                agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs)
            try:
                attr_value = agg_inx[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                tmp = copy.deepcopy(i)
                while attr_value >= k and i[0][-1] != intvl_rv[-1]:
                    tmp = copy.deepcopy(i)
                    i[0].append(intvl_rv[intvl_rv.index(i[0][-1])+1])
                    inx,tia_inx = Intersection_Static(nodes_df,edges_df,invar,i[0]+i[1])
                    if inx[1].empty:
                        break
                    agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs)
                    try:
                        attr_value = agg_inx[1].loc[values][0]
                    except:
                        attr_value = 0
                    if attr_value >= k:
                        tmp = copy.deepcopy(i)
                stabI_a.append(tmp)
    elif attrtype == 'Variant':
        for i in stabI_invl_a:
            inx,tva_inx = Intersection_Variant(nodes_df,edges_df,varying,i[0]+i[1])
            if inx[1].empty:
                continue
            else:
                agg_inx = Aggregate_Variant_Dist(inx,tva_inx,i[0]+i[1])
            try:
                attr_value = agg_inx[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                tmp = copy.deepcopy(i)
                while attr_value >= k and i[0][-1] != intvl_rv[-1]:
                    tmp = copy.deepcopy(i)
                    i[0].append(intvl_rv[intvl_rv.index(i[0][-1])+1])
                    inx,tva_inx = Intersection_Variant(nodes_df,edges_df,varying,i[0]+i[1])
                    if inx[1].empty:
                        break
                    agg_inx = Aggregate_Variant_Dist(inx,tva_inx,i[0]+i[1])
                    try:
                        attr_value = agg_inx[1].loc[values][0]
                    except:
                        attr_value = 0
                    if attr_value >= k:
                        tmp = copy.deepcopy(i)
                stabI_a.append(tmp)
    else:
        for i in stabI_invl_a:
            inx,tia_inx,tva_inx = Intersection_Mix(nodes_df,edges_df,invar,varying,i[0]+i[1])
            if inx[1].empty:
                continue
            else:
                agg_inx = Aggregate_Mix_Dist(inx,tva_inx,tia_inx,stc_attrs,i[0]+i[1])
            try:
                attr_value = agg_inx[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                tmp = copy.deepcopy(i)
                while attr_value >= k and i[0][-1] != intvl_rv[-1]:
                    tmp = copy.deepcopy(i)
                    i[0].append(intvl_rv[intvl_rv.index(i[0][-1])+1])
                    inx,tia_inx,tva_inx = Intersection_Mix(nodes_df,edges_df,invar,varying,i[0]+i[1])
                    if inx[1].empty:
                        break
                    agg_inx = Aggregate_Mix_Dist(inx,tva_inx,tia_inx,stc_attrs,i[0]+i[1])
                    try:
                        attr_value = agg_inx[1].loc[values][0]
                    except:
                        attr_value = 0
                    if attr_value >= k:
                        tmp = copy.deepcopy(i)
                stabI_a.append(tmp)      
    stabI_a = [[i[::-1],j] for i,j in stabI_a]
    return(stabI_a,agg_inx)






# Stability | Inx Semantics
# a Old(INX)&New
def Stability_Intersection_Static_a(k,intvl,nodes_df,edges_df,invar,stc_attrs,values):
    intvl_rv = intvl[::-1]
    stabI_invl_a = []
    for i in intvl[:-1]:
        stabI_invl_a.append([[i],[intvl[intvl.index(i)+1]]])  
    stabI_a = []
    for i in stabI_invl_a:
        inx,tia_inx = Intersection_Static(nodes_df,edges_df,invar,i[0]+i[1])
        if inx[1].empty:
            continue
        else:
            agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs)
        try:
            attr_value = agg_inx[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            tmp = copy.deepcopy(i)
            while attr_value >= k and i[0][-1] != intvl_rv[-1]:
                tmp = copy.deepcopy(i)
                i[0].append(intvl_rv[intvl_rv.index(i[0][-1])+1])
                inx,tia_inx = Intersection_Static(nodes_df,edges_df,invar,i[0]+i[1])
                if inx[1].empty:
                    break
                agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs)
                try:
                    attr_value = agg_inx[1].loc[values][0]
                except:
                    attr_value = 0
                if attr_value >= k:
                    tmp = copy.deepcopy(i)
            stabI_a.append(tmp)
    stabI_a = [[i[::-1],j] for i,j in stabI_a]
    return(stabI_a,agg_inx)


def Stability_Intersection_Variant_a(k,intvl,nodes_df,edges_df,varying,values):
    intvl_rv = intvl[::-1]
    stabI_invl_a = []
    for i in intvl[:-1]:
        stabI_invl_a.append([[i],[intvl[intvl.index(i)+1]]])  
    stabI_a = []
    for i in stabI_invl_a:
        inx,tva_inx = Intersection_Variant(nodes_df,edges_df,varying,i[0]+i[1])
        if inx[1].empty:
            continue
        else:
            agg_inx = Aggregate_Variant_Dist(inx,tva_inx,i[0]+i[1])
        try:
            attr_value = agg_inx[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            tmp = copy.deepcopy(i)
            while attr_value >= k and i[0][-1] != intvl_rv[-1]:
                tmp = copy.deepcopy(i)
                i[0].append(intvl_rv[intvl_rv.index(i[0][-1])+1])
                inx,tva_inx = Intersection_Variant(nodes_df,edges_df,varying,i[0]+i[1])
                if inx[1].empty:
                    break
                agg_inx = Aggregate_Variant_Dist(inx,tva_inx,i[0]+i[1])
                try:
                    attr_value = agg_inx[1].loc[values][0]
                except:
                    attr_value = 0
                if attr_value >= k:
                    tmp = copy.deepcopy(i)
            stabI_a.append(tmp)
    stabI_a = [[i[::-1],j] for i,j in stabI_a]
    return(stabI_a,agg_inx)


def Stability_Intersection_Mix_a(k,intvl,nodes_df,edges_df,invar,varying,stc_attrs,values):
    intvl_rv = intvl[::-1]
    stabI_invl_a = []
    for i in intvl[:-1]:
        stabI_invl_a.append([[i],[intvl[intvl.index(i)+1]]])  
    stabI_a = []
    for i in stabI_invl_a:
        inx,tia_inx,tva_inx = Intersection_Mix(nodes_df,edges_df,invar,varying,i[0]+i[1])
        if inx[1].empty:
            continue
        else:
            agg_inx = Aggregate_Mix_Dist(inx,tva_inx,tia_inx,stc_attrs,i[0]+i[1])
        try:
            attr_value = agg_inx[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            tmp = copy.deepcopy(i)
            while attr_value >= k and i[0][-1] != intvl_rv[-1]:
                tmp = copy.deepcopy(i)
                i[0].append(intvl_rv[intvl_rv.index(i[0][-1])+1])
                inx,tia_inx,tva_inx = Intersection_Mix(nodes_df,edges_df,invar,varying,i[0]+i[1])
                if inx[1].empty:
                    break
                agg_inx = Aggregate_Mix_Dist(inx,tva_inx,tia_inx,stc_attrs,i[0]+i[1])
                try:
                    attr_value = agg_inx[1].loc[values][0]
                except:
                    attr_value = 0
                if attr_value >= k:
                    tmp = copy.deepcopy(i)
            stabI_a.append(tmp)      
    stabI_a = [[i[::-1],j] for i,j in stabI_a]
    return(stabI_a,agg_inx)



# Growth | Union Semantics
# a New-Old(UNION)
def Growth_Union_a(k,intvl,nodes_df,edges_df,invar,varying,attrtype,stc_attrs,values):
    growth_invl_a = []
    for i in intvl[:-1]:
        growth_invl_a.append([[intvl[intvl.index(i)+1]],[i]])  
    growth_a = []
    for i in growth_invl_a:
        if attrtype == 'Static':
            diff,tia_d = Diff_Static(nodes_df,edges_df,invar,i[0],i[1])
            agg = Aggregate_Static_Dist(diff,tia_d,stc_attrs)
            diff_agg = Diff_Post_Agg_Static(agg,stc_attrs)
            try:
                attr_value = diff_agg[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                growth_a.append(i)
        elif attrtype == 'Variant':
            diff,tva_d = Diff_Variant(nodes_df,edges_df,varying,i[0],i[1])
            agg = Aggregate_Variant_Dist(diff,tva_d,i[0])
            diff_agg = Diff_Post_Agg_Variant(agg)
            try:
                attr_value = diff_agg[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                growth_a.append(i)
        else:
            diff,tia_d,tva_d = Diff_Mix(nodes_df,edges_df,invar,varying,i[0],i[1])
            agg = Aggregate_Mix_Dist(diff,tva_d,tia_d,stc_attrs,i[0])
            diff_agg = Diff_Post_Agg_Mix(agg,stc_attrs)
            try:
                attr_value = diff_agg[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                growth_a.append(i)
    return(growth_a,diff_agg)





# Growth | Union Semantics
# a New-Old(UNION)
def Growth_Union_Static_a(k,intvl,nodes_df,edges_df,invar,stc_attrs,values):
    growth_invl_a = []
    for i in intvl[:-1]:
        growth_invl_a.append([[intvl[intvl.index(i)+1]],[i]])  
    growth_a = []
    for i in growth_invl_a:
        diff,tia_d = Diff_Static(nodes_df,edges_df,invar,i[0],i[1])
        agg = Aggregate_Static_Dist(diff,tia_d,stc_attrs)
        diff_agg = Diff_Post_Agg_Static(agg,stc_attrs)
        try:
            attr_value = diff_agg[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            growth_a.append(i)
    return(growth_a,diff_agg)


def Growth_Union_Variant_a(k,intvl,nodes_df,edges_df,values):
    growth_invl_a = []
    for i in intvl[:-1]:
        growth_invl_a.append([[intvl[intvl.index(i)+1]],[i]])  
    growth_a = []
    for i in growth_invl_a:
        diff,tva_d = Diff_Variant(nodes_df,edges_df,varying,i[0],i[1])
        agg = Aggregate_Variant_Dist(diff,tva_d,i[0])
        diff_agg = Diff_Post_Agg_Variant(agg)
        try:
            attr_value = diff_agg[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            growth_a.append(i)
    return(growth_a,diff_agg)


def Growth_Union_Mix_a(k,intvl,nodes_df,edges_df,invar,varying,stc_attrs,values):
    growth_invl_a = []
    for i in intvl[:-1]:
        growth_invl_a.append([[intvl[intvl.index(i)+1]],[i]])  
    growth_a = []
    for i in growth_invl_a:
        diff,tia_d,tva_d = Diff_Mix(nodes_df,edges_df,invar,varying,i[0],i[1])
        agg = Aggregate_Mix_Dist(diff,tva_d,tia_d,stc_attrs,i[0])
        diff_agg = Diff_Post_Agg_Mix(agg,stc_attrs)
        try:
            attr_value = diff_agg[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            growth_a.append(i)
    return(growth_a,diff_agg)







# Shrinkage | Union Semantics
def Shrink_Union_a(k,intvl,nodes_df,edges_df,invar,varying,attrtype,stc_attrs,values):
    shrink_invl_a = []
    for i in intvl[:-1]:
        shrink_invl_a.append([[i],[intvl[intvl.index(i)+1]]])
    shrink_invl_a.reverse()
    shrink_a = []
    for i in shrink_invl_a:
        if attrtype == 'Static':
            diff,tia_d = Diff_Static(nodes_df,edges_df,invar,i[0],i[1])
            agg = Aggregate_Static_Dist(diff,tia_d,stc_attrs)
            diff_agg = Diff_Post_Agg_Static(agg,stc_attrs)
            try:
                attr_value = diff_agg[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                shrink_a.append(i)
            else:
                while attr_value < k and i[-1][0] != intvl[-1]:
                    if intvl[intvl.index(i[0][-1])+1] not in [j[0][-1] for j in shrink_a] \
                and intvl[intvl.index(i[0][-1])+2] not in [j[1][0] for j in shrink_a]:
                        i[0].append(intvl[intvl.index(i[0][-1])+1])
                        i[1] = [intvl[intvl.index(i[0][-1])+1]]
                        diff,tia_d = Diff_Static(nodes_df,edges_df,invar,i[0],i[1])
                        agg = Aggregate_Static_Dist(diff,tia_d,stc_attrs)
                        diff_agg = Diff_Post_Agg_Static(agg,stc_attrs)
                        try:
                            attr_value = diff_agg[1].loc[values][0]
                        except:
                            attr_value = 0
                    else:
                        break
                if attr_value >= k:
                    shrink_a.append(i)
        if attrtype == 'Variant':
            diff,tva_d = Diff_Variant(nodes_df,edges_df,varying,i[0],i[1])
            agg = Aggregate_Variant_Dist(diff,tva_d,i[0])
            diff_agg = Diff_Post_Agg_Variant(agg)
            try:
                attr_value = diff_agg[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                shrink_a.append(i)
            else:
                while attr_value < k and i[-1][0] != intvl[-1]:
                    if intvl[intvl.index(i[0][-1])+1] not in [j[0][-1] for j in shrink_a] \
                and intvl[intvl.index(i[0][-1])+2] not in [j[1][0] for j in shrink_a]:
                        i[0].append(intvl[intvl.index(i[0][-1])+1])
                        i[1] = [intvl[intvl.index(i[0][-1])+1]]
                        diff,tva_d = Diff_Variant(nodes_df,edges_df,varying,i[0],i[1])
                        agg = Aggregate_Variant_Dist(diff,tva_d,i[0])
                        diff_agg = Diff_Post_Agg_Variant(agg)
                        try:
                            attr_value = diff_agg[1].loc[values][0]
                        except:
                            attr_value = 0
                    else:
                        break
                if attr_value >= k:
                    shrink_a.append(i)
        else:
            diff,tia_d,tva_d = Diff_Mix(nodes_df,edges_df,invar,varying,i[0],i[1])
            agg = Aggregate_Mix_Dist(diff,tva_d,tia_d,stc_attrs,i[0])
            diff_agg = Diff_Post_Agg_Mix(agg,stc_attrs)
            try:
                attr_value = diff_agg[1].loc[values][0]
            except:
                attr_value = 0
            if attr_value >= k:
                shrink_a.append(i)
            else:
                while attr_value < k and i[-1][0] != intvl[-1]:
                    if intvl[intvl.index(i[0][-1])+1] not in [j[0][-1] for j in shrink_a] \
                and intvl[intvl.index(i[0][-1])+2] not in [j[1][0] for j in shrink_a]:
                        i[0].append(intvl[intvl.index(i[0][-1])+1])
                        i[1] = [intvl[intvl.index(i[0][-1])+1]]
                        diff,tia_d,tva_d = Diff_Mix(nodes_df,edges_df,invar,varying,i[0],i[1])
                        agg = Aggregate_Mix_Dist(diff,tva_d,tia_d,stc_attrs,i[0])
                        diff_agg = Diff_Post_Agg_Mix(agg,stc_attrs)
                        try:
                            attr_value = diff_agg[1].loc[values][0]
                        except:
                            attr_value = 0
                    else:
                        break
                if attr_value >= k:
                    shrink_a.append(i)
    return(shrink_a,diff_agg)










# Shrinkage | Union Semantics | Static
def Shrink_Union_Static_a(k,intvl,nodes_df,edges_df,invar,stc_attrs,values):
    shrink_invl_a = []
    for i in intvl[:-1]:
        shrink_invl_a.append([[i],[intvl[intvl.index(i)+1]]])
    shrink_invl_a.reverse()
    shrink_a = []
    for i in shrink_invl_a:
        diff,tia_d = Diff_Static(nodes_df,edges_df,invar,i[0],i[1])
        agg = Aggregate_Static_Dist(diff,tia_d,stc_attrs)
        diff_agg = Diff_Post_Agg_Static(agg,stc_attrs)
        try:
            attr_value = diff_agg[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            shrink_a.append(i)
        else:
            while attr_value < k and i[-1][0] != intvl[-1]:
                if intvl[intvl.index(i[0][-1])+1] not in [j[0][-1] for j in shrink_a] \
            and intvl[intvl.index(i[0][-1])+2] not in [j[1][0] for j in shrink_a]:
                    i[0].append(intvl[intvl.index(i[0][-1])+1])
                    i[1] = [intvl[intvl.index(i[0][-1])+1]]
                    diff,tia_d = Diff_Static(nodes_df,edges_df,invar,i[0],i[1])
                    agg = Aggregate_Static_Dist(diff,tia_d,stc_attrs)
                    diff_agg = Diff_Post_Agg_Static(agg,stc_attrs)
                    try:
                        attr_value = diff_agg[1].loc[values][0]
                    except:
                        attr_value = 0
                else:
                    break
            if attr_value >= k:
                shrink_a.append(i)
    return(shrink_a,diff_agg)
                    
def Shrink_Union_Variant_a(k,intvl,nodes_df,edges_df,varying,values):
    shrink_invl_a = []
    for i in intvl[:-1]:
        shrink_invl_a.append([[i],[intvl[intvl.index(i)+1]]])
    shrink_invl_a.reverse()
    shrink_a = []
    for i in shrink_invl_a:
        diff,tva_d = Diff_Variant(nodes_df,edges_df,varying,i[0],i[1])
        agg = Aggregate_Variant_Dist(diff,tva_d,i[0])
        diff_agg = Diff_Post_Agg_Variant(agg)
        try:
            attr_value = diff_agg[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            shrink_a.append(i)
        else:
            while attr_value < k and i[-1][0] != intvl[-1]:
                if intvl[intvl.index(i[0][-1])+1] not in [j[0][-1] for j in shrink_a] \
            and intvl[intvl.index(i[0][-1])+2] not in [j[1][0] for j in shrink_a]:
                    i[0].append(intvl[intvl.index(i[0][-1])+1])
                    i[1] = [intvl[intvl.index(i[0][-1])+1]]
                    diff,tva_d = Diff_Variant(nodes_df,edges_df,varying,i[0],i[1])
                    agg = Aggregate_Variant_Dist(diff,tva_d,i[0])
                    diff_agg = Diff_Post_Agg_Variant(agg)
                    try:
                        attr_value = diff_agg[1].loc[values][0]
                    except:
                        attr_value = 0
                else:
                    break
            if attr_value >= k:
                shrink_a.append(i)
    return(shrink_a,diff_agg)

def Shrink_Union_Mix_a(k,intvl,nodes_df,edges_df,invar,varying,stc_attrs,values):
    shrink_invl_a = []
    for i in intvl[:-1]:
        shrink_invl_a.append([[i],[intvl[intvl.index(i)+1]]])
    shrink_invl_a.reverse()
    shrink_a = []
    for i in shrink_invl_a:
        diff,tia_d,tva_d = Diff_Mix(nodes_df,edges_df,invar,varying,i[0],i[1])
        agg = Aggregate_Mix_Dist(diff,tva_d,tia_d,stc_attrs,i[0])
        diff_agg = Diff_Post_Agg_Mix(agg,stc_attrs)
        try:
            attr_value = diff_agg[1].loc[values][0]
        except:
            attr_value = 0
        if attr_value >= k:
            shrink_a.append(i)
        else:
            while attr_value < k and i[-1][0] != intvl[-1]:
                if intvl[intvl.index(i[0][-1])+1] not in [j[0][-1] for j in shrink_a] \
            and intvl[intvl.index(i[0][-1])+2] not in [j[1][0] for j in shrink_a]:
                    i[0].append(intvl[intvl.index(i[0][-1])+1])
                    i[1] = [intvl[intvl.index(i[0][-1])+1]]
                    diff,tia_d,tva_d = Diff_Mix(nodes_df,edges_df,invar,varying,i[0],i[1])
                    agg = Aggregate_Mix_Dist(diff,tva_d,tia_d,stc_attrs,i[0])
                    diff_agg = Diff_Post_Agg_Mix(agg,stc_attrs)
                    try:
                        attr_value = diff_agg[1].loc[values][0]
                    except:
                        attr_value = 0
                else:
                    break
            if attr_value >= k:
                shrink_a.append(i)
    return(shrink_a,diff_agg)







# F - F exploration
if __name__ == '__main__':
    filename = sys.argv[1]
    
    #DBLP
    if filename == 'dblp_dataset':
        # READ edges, nodes, static and variant attributes from csv
        edges_df = pd.read_csv(filename + '/edges.csv', sep=' ', index_col=[0,1])
        nodes_df = pd.read_csv(filename + '/nodes.csv', sep=' ', index_col=0)
        time_variant_attr = pd.read_csv(filename + '/time_variant_attr.csv', sep=' ', index_col=0)
        time_invariant_attr = pd.read_csv(filename + '/time_invariant_attr.csv', sep=' ', index_col=0)
        time_invariant_attr.rename(columns={'0': 'gender'}, inplace=True)
        nodes_df.index.names = ['userID']
        time_invariant_attr.gender.replace(['female','male'], ['F','M'],inplace=True)
        intvl = [str(i) for i in range(2000,2021)]
        # intersection
        intvl_pairs = [[i,intvl[intvl.index(i)+1]] for i in intvl[:-1]]
        inx_pairs = []
        for i in intvl_pairs:
            inx,tia_inx = Intersection_Static(nodes_df,edges_df,time_invariant_attr,i)
            agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs=['gender'])
            inx_pairs.append(agg_inx[1].loc['F','F'][0])
        #k=max(inx_pairs)
        stabI_a_k1 = Stability_Intersection_a(max(inx_pairs),intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(inx_pairs)/2
        stabI_a_k2 = Stability_Intersection_a(max(inx_pairs)/2,intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(inx_pairs)/62
        stabI_a_k3 = Stability_Intersection_a(max(inx_pairs)/62,intvl,nodes_df,edges_df,time_invariant_attr)
        stabInx_a = [stabI_a_k1] + [stabI_a_k2] + [stabI_a_k3]
        # difference growth
        diff_pairs_G = []
        for i in intvl_pairs:
            diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,[i[1]],[i[0]])
            agg_diff_G = Aggregate_Static_Dist(diff,tia_diff,stc_attrs=['gender'])
            diff_pairs_G.append(agg_diff_G[1].loc['F','F'][0])
        #k=max(diff_pairs_G)
        growthU_a_k1 = Growth_Union_a(max(diff_pairs_G),intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)/3
        growthU_a_k2 = Growth_Union_a(max(diff_pairs_G)/3,intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)/10
        growthU_a_k3 = Growth_Union_a(max(diff_pairs_G)/10,intvl,nodes_df,edges_df,time_invariant_attr)
        growthU_a = [growthU_a_k1] + [growthU_a_k2] + [growthU_a_k3]
        # difference shrinkage
        diff_pairs_S = []
        for i in intvl_pairs:
            diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,[i[0]],[i[1]])
            agg_diff_G = Aggregate_Static_Dist(diff,tia_diff,stc_attrs=['gender'])
            diff_pairs_S.append(agg_diff_G[1].loc['F','F'][0])
        #k=max(diff_pairs_G)
        shrinkU_a_k1 = Shrink_Union_a(min(diff_pairs_S),intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)*5
        shrinkU_a_k2 = Shrink_Union_a(min(diff_pairs_S)*5,intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)*20
        shrinkU_a_k3 = Shrink_Union_a(min(diff_pairs_S)*20,intvl,nodes_df,edges_df,time_invariant_attr)
        shrinkU_a = [shrinkU_a_k1] + [shrinkU_a_k2] + [shrinkU_a_k3]
    
    
    # MovieLens
    if filename == 'movielens_dataset':
        # READ edges, nodes, static and variant attributes from csv
        edges_df = pd.read_csv(filename + '/edges.csv', sep=' ')
        edges_df.set_index(['Left', 'Right'], inplace=True)
        nodes_df = pd.read_csv(filename + '/nodes.csv', sep=' ', index_col=0)
        time_variant_attr = pd.read_csv(filename + '/time_variant_attr.csv', sep=' ', index_col=0)
        time_invariant_attr = pd.read_csv(filename + '/time_invariant_attr.csv', sep=' ', index_col=0)
        intvl = ['may','jun','jul','aug','sep','oct']
        # intersection
        intvl_pairs = [[i,intvl[intvl.index(i)+1]] for i in intvl[:-1]]
        inx_pairs = []
        for i in intvl_pairs:
            inx,tia_inx = Intersection_Static(nodes_df,edges_df,time_invariant_attr,i)
            agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs=['gender'])
            inx_pairs.append(agg_inx[1].loc['F','F'][0])
        #k=max(inx_pairs)
        stabI_a_k1 = Stability_Intersection_a(max(inx_pairs),intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(inx_pairs)/2
        stabI_a_k2 = Stability_Intersection_a(max(inx_pairs)/2,intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(inx_pairs)/62
        stabI_a_k3 = Stability_Intersection_a(max(inx_pairs)/86,intvl,nodes_df,edges_df,time_invariant_attr)
        stabInx_a = [stabI_a_k1] + [stabI_a_k2] + [stabI_a_k3]
        # difference growth
        diff_pairs_G = []
        for i in intvl_pairs:
            diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,[i[1]],[i[0]])
            agg_diff_G = Aggregate_Static_Dist(diff,tia_diff,stc_attrs=['gender'])
            diff_pairs_G.append(agg_diff_G[1].loc['F','F'][0])
        #k=max(diff_pairs_G)
        growthU_a_k1 = Growth_Union_a(max(diff_pairs_G),intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)/2
        growthU_a_k2 = Growth_Union_a(max(diff_pairs_G)/2,intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)/12
        growthU_a_k3 = Growth_Union_a(max(diff_pairs_G)/12,intvl,nodes_df,edges_df,time_invariant_attr)
        growthU_a = [growthU_a_k1] + [growthU_a_k2] + [growthU_a_k3]
        # difference shrinkage
        diff_pairs_S = []
        for i in intvl_pairs:
            diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,[i[0]],[i[1]])
            agg_diff_G = Aggregate_Static_Dist(diff,tia_diff,stc_attrs=['gender'])
            diff_pairs_S.append(agg_diff_G[1].loc['F','F'][0])
        #k=max(diff_pairs_G)
        shrinkU_a_k1 = Shrink_Union_a(min(diff_pairs_S),intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)*2
        shrinkU_a_k2 = Shrink_Union_a(min(diff_pairs_S)*2,intvl,nodes_df,edges_df,time_invariant_attr)
        #k=max(diff_pairs_G)*5
        shrinkU_a_k3 = Shrink_Union_a(min(diff_pairs_S)*5,intvl,nodes_df,edges_df,time_invariant_attr)
        shrinkU_a = [shrinkU_a_k1] + [shrinkU_a_k2] + [shrinkU_a_k3]
    
    
    
    
    #save output for stability 
    pd.DataFrame(stabInx_a).to_csv('out_stabInx_a.txt', sep=' ', mode='w')
    #save output for growth
    pd.DataFrame(growthU_a).to_csv('out_growthU_a.txt', sep=' ', mode='w')
    #save output for shrinkage
    pd.DataFrame(shrinkU_a).to_csv('out_shrinkU_a.txt', sep=' ', mode='w')






