import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph
import pandas as pd
import numpy as np
import sys
sys.path.insert(1, 'graphtempo')
from graphtempo import *
from exploration import *
import time
from PIL import Image
import plotly.express as px
import copy
import networkx as nx
from littleballoffur.exploration_sampling import SnowBallSampler


st.set_page_config(layout='wide')
#image = Image.open('logo/app_logo.png')




# from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
# from htbuilder.units import percent, px
# from htbuilder.funcs import rgba, rgb


# def image(src_as_string, **style):
#     return img(src=src_as_string, style=styles(**style))


# def link(link, text, **style):
#     return a(_href=link, _target="_blank", style=styles(**style))(text)


# def layout(*args):

#     style = """
#     <style>
#       # MainMenu {visibility: hidden;}
#       footer {visibility: hidden;}
#      .stApp { bottom: 105px; }
#     </style>
#     """

#     style_div = styles(
#         position="fixed",
#         left=0,
#         bottom=0,
#         margin=px(0, 0, 0, 0),
#         width=percent(100),
#         color="black",
#         text_align="center",
#         height="auto",
#         opacity=1
#     )

#     style_hr = styles(
#         display="block",
#         margin=px(8, 8, "auto", "auto"),
#         border_style="inset",
#         border_width=px(2)
#     )

#     body = p()
#     foot = div(
#         style=style_div
#     )(
#         hr(
#             style=style_hr
#         ),
#         body
#     )

#     st.markdown(style, unsafe_allow_html=True)

#     for arg in args:
#         if isinstance(arg, str):
#             body(arg)

#         elif isinstance(arg, HtmlElement):
#             body(arg)

#     st.markdown(str(foot), unsafe_allow_html=True)

# def footer():
#     myargs = [
#         image('http://graphtempo.eu/assets/img/logo.png',
#               width=px(150), height=px(50)),
#     ]
#     layout(*myargs)


# if __name__ == "__main__":
#     footer()




@st.experimental_memo
def read_data(edgesdf,time_var,time_invar,timepoint):
	# get indexes of edges_df where first column value is not 0.
	edges = edges_df.loc[:,timepoint][edges_df.loc[:,timepoint]!=0].index.tolist()
	# get undirected graph for the edges
	G = nx.Graph()
	G.add_edges_from(edges)
	# get lcc for G: G0
	G0 = G.subgraph(max(nx.connected_components(G), key=len))
	# map edges index to number
	# get nodes of the lcc
	nodes_G0 = list(G0.nodes)
	node_num_map = {nodes_G0[i]:i for i in range(len(nodes_G0))}
	num_node_map = {i:nodes_G0[i] for i in range(len(nodes_G0))}
	edges_G0 = list(G0.edges)
	edges_G0 = [[node_num_map[i[0]],node_num_map[i[1]]] for i in edges_G0]
	G0 = nx.Graph()
	G0.add_edges_from(edges_G0)

	if nx.density(G0)> 0.5:
		num_of_nodes = 30
	else:
		num_of_nodes = 100
	if len(nodes_G0)>num_of_nodes:
		# call sampler
		sampling_flag = True
		sampler = SnowBallSampler(num_of_nodes)
		sampled_graph = sampler.sample(G0)
	else:
		sampling_flag = False
		sampled_graph = copy.deepcopy(G0)

	sampled_edges_initial = [(num_node_map[i[0]],num_node_map[i[1]]) for i in list(sampled_graph.edges)]
	sampled_edges = []
	for e in sampled_edges_initial:
		if e[::-1] in edges:
			sampled_edges.append(e[::-1])
	sampled_edges.extend(sampled_edges_initial)
	sampled_edges = pd.DataFrame(sampled_edges)
	sampled_edges = sampled_edges.values.tolist()
	sampled_nodes = [num_node_map[i] for i in list(sampled_graph.nodes)]
	sampled_attrs = time_invar[time_invar.index.isin(sampled_nodes)]
	if not isinstance(time_var,list):
		sampled_attrs['varying'] = time_var.loc[:,timepoint]
	sampled_attrs = sampled_attrs.reset_index()
	return(sampled_edges,sampled_nodes,sampled_attrs,sampling_flag)

def create_Graph(aggregation,color_palette,flag):
	idx_nodes = aggregation[0].index.tolist()
	idx_nodes = [[i] if not isinstance(i,tuple) else i for i in idx_nodes]
	idx_nodes = [[str(i) for i in idx] for idx in idx_nodes]
	idx_nodes = ['|'.join(i) for i in idx_nodes]
	idx_edges = aggregation[1].index.tolist()
	idx_edges = [[str(i) for i in lst] for lst in idx_edges]
	idx_edges = [tuple([tuple(i[:len(i)//2]),tuple(i[len(i)//2:])]) for i in idx_edges]
	idx_edges = [tuple(['|'.join(i[0]),'|'.join(i[1])]) for i in idx_edges]

	if len(idx_nodes) > len(color_palette):
		color_palette = color_palette*(int(len(idx_nodes)/len(color_palette) + 1))
	
	for i,df in enumerate(aggregation):
		if i==0:
			aggregation[i].index = idx_nodes
		if i==1:
			multi_idx = pd.MultiIndex.from_tuples(idx_edges)
			aggregation[i].index = multi_idx

	wrong_edge_idxes = []
	wrong_node_idxes = []
	for node in idx_nodes:
		if aggregation[0].loc[node,:][0] == 0:
			wrong_node_idxes.append(node)
			for edge in idx_edges:
				if node in edge:
					wrong_edge_idxes.append(edge)

	right_edge_idxes = [i for i in idx_edges if i not in wrong_edge_idxes]
	agg_edges = aggregation[1].loc[right_edge_idxes]
	idx_edges = agg_edges.index.tolist()

	right_node_idxes = [i for i in idx_nodes if i not in wrong_node_idxes]
	agg_nodes = aggregation[0].loc[right_node_idxes]
	idx_nodes = agg_nodes.index.tolist()

	nodes_agg_graph = []
	inx = 0
	for node in idx_nodes:
		if flag == 0:
			nodes_agg_graph.append(Node(id=node,
				  #size=15,
				  title=node,
				  label=str(agg_nodes.loc[node][0]),
				  symbolType='dot',
				  font={'enabled':True,'color':color_palette[inx]},
				  physics=False,
	              color={'border':'black','background':color_palette[inx]})
			)
		elif flag == 1:
			nodes_agg_graph.append(Node(id=node,
				  #size=15,
				  title=node,
				  label='-'+str(agg_nodes.loc[node][0]),
				  symbolType='dot',
				  font={'enabled':True,'color':color_palette[inx]},
				  physics=False,
	              color={'border':'black','background':color_palette[inx]})
			)
		else:
			nodes_agg_graph.append(Node(id=node,
				  #size=15,
				  title=node,
				  label='+'+str(agg_nodes.loc[node][0]),
				  symbolType='dot',
				  font={'enabled':True,'color':color_palette[inx]},
				  physics=False,
	              color={'border':'black','background':color_palette[inx]})
			)
		inx += 1
	edges_agg_graph = []
	for edge in idx_edges:
		if flag == 0:
			edges_agg_graph.append(
	            Edge(source=edge[0],
	            	 label=str(agg_edges.loc[edge][0]),
	                 target=edge[1], 
	                 #smooth=False,
	                 smooth= {'enabled':True,'type':'dynamic'},
	                 font={'color':'black'},
	                 length=300,
	                 color='black')
	        )
		elif flag == 1:
			edges_agg_graph.append(
	            Edge(source=edge[0],
	            	 label='-'+str(agg_edges.loc[edge][0]),
	                 target=edge[1], 
	                 #smooth=False,
	                 smooth= {'enabled':True,'type':'dynamic'},
	                 font={'color':'black'},
	                 length=300,
	                 color='black')
	        )
		else:
			edges_agg_graph.append(
	            Edge(source=edge[0],
	            	 label='+'+str(agg_edges.loc[edge][0]),
	                 target=edge[1], 
	                 #smooth=False,
	                 smooth= {'enabled':True,'type':'dynamic'},
	                 font={'color':'black'},
	                 length=300,
	                 color='black')
	        )

	config = Config(width=1000, 
	                height=500,
	                #graphviz_layout='neato',
	                #graphviz_layout=layout,
	                #graphviz_config={"rankd": rankdir, "ranks": ranksep, "nodese": nodesep},
	                directed=True,
	                nodeHighlightBehavior=True, 
	                highlightColor="#F7A7A6",
	                collapsible=True,
	                node={'labelProperty':'label'},
	                link={'labelProperty': 'label', 'renderLabel': True},
	                maxZoom=2,
	                minZoom=0.1,
	                staticGraphWithDragAndDrop=False,
	                staticGraph=False,
	                initialZoom=1
	                )

	return_value = agraph(nodes=nodes_agg_graph, 
	                      edges=edges_agg_graph, 
	                      config=config)

st.sidebar.title("GraphTempo")
app_mode = st.sidebar.selectbox("Choose mode",
    ["Show instructions", "Graph Overview", "Graph Aggregation", "Graph Exploration"])

if app_mode == "Show instructions":
    st.sidebar.success('To continue select "Graph Overview".')
    with st.container():
    	i=100
    	st.subheader('Aggregation and Exploration for Evolving Graphs')
    	#st.subheader('Implementation of the paper GraphTempo: An aggregation framework for evolving graphs')
    	st.write('We provide three real-world datasets for testing the tasks of aggregation and exploration. Alternatively, the user can upload his/her own dataset providing it follows the appropriate format. The main functions are:')
    	st.write('**Graph Overview**: provides a view of the original graph on the selected time point and attribute. When nodes in the graph are more than', i, ', we sample the graph by applying the Snowball Sampling algorithm.')
    	st.write('**Graph Aggregation**: facilitates aggregation on specific periods of time for one or more node attributes. The available temporal operators form a different temporal graph based on the semantics of each operator. The user can choose between two types of aggregation.')
    	st.write('**Graph Exploration**: discovers intervals in the graph as to important events. The user can choose the preferred event, the type of the edge by selecting the values of the attributes interested and the number of the preferred interactions.')
    	st.write('???? To continue select "Graph Overview".')
	

elif app_mode == "Graph Overview":
	with st.sidebar:
		#Choose Dataset
		st.title('Dataset')
		dataset = st.selectbox('Choose dataset',['DBLP','MovieLens','Primary School'])
		if dataset == 'DBLP':
			stc = ['Gender']
			varying = ['#Publications']
			edges_df = pd.read_csv('datasets/dblp_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/dblp_dataset/nodes.csv', sep=' ', index_col=0)
			time_variant_attr = pd.read_csv('datasets/dblp_dataset/time_variant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/dblp_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr.rename(columns={'0': 'gender'}, inplace=True)
			nodes_df.index.names = ['userID']
			time_invariant_attr.gender.replace(['female','male'], ['F','M'],inplace=True)
		elif dataset == 'MovieLens':
			stc = ['Gender','Age','Occupation']
			varying = ['Rating']
			edges_df = pd.read_csv('datasets/movielens_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/movielens_dataset/nodes.csv', sep=' ', index_col=0)
			time_variant_attr = pd.read_csv('datasets/movielens_dataset/time_variant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/movielens_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
		elif dataset == 'Primary School':
			stc = ['Gender','Class']
			edges_df = pd.read_csv('datasets/school_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/school_dataset/nodes.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/school_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
			time_variant_attr = []
			varying = []
		period = list(edges_df.columns)

		with st.expander('Load your dataset'):
			uploaded_files = st.file_uploader("Choose a CSV file", type='csv', accept_multiple_files=True)
			for uploaded_file in uploaded_files:
				if uploaded_file.name == 'edges.csv':
					edges_df = pd.read_csv(uploaded_file, sep=' ', index_col=[0,1])
				if uploaded_file.name == 'nodes.csv':
					nodes_df = pd.read_csv(uploaded_file, sep=' ', index_col=0)
				if uploaded_file.name == 'time_variant_attr.csv':
					time_variant_attr = pd.read_csv(uploaded_file, sep=' ', index_col=0)
				if uploaded_file.name == 'time_invariant_attr.csv':
					time_invariant_attr = pd.read_csv(uploaded_file, sep=' ', index_col=0)
		
				period = list(edges_df.columns)
				stc = list(time_invariant_attr.columns)
				varying = ['varying']

		# View graph
		st.title('Set up Overview')
		time_sel = st.select_slider('Time point', options=period)
		attributes_sel = st.selectbox('Attribute',stc+varying)
		edges,nodes,attr,sampling_flag = read_data(edges_df,time_variant_attr,time_invariant_attr,time_sel)
		attr = attr.astype(str)
		attr.columns = ['UserID']+stc+varying
		if attributes_sel:
			nodes_per_attr_value_dct = attr.groupby(attributes_sel)['UserID'].apply(list).to_dict()
		submitted_view = st.button('View')

	with st.container():
		if time_sel and attributes_sel and submitted_view:
			with st.spinner('Wait for it...'):
				time.sleep(3)

			if sampling_flag == True:
				sampling = True
			else:
				sampling = False
			st.subheader('Graph Overview')
			#st.subheader('Graph view over time and attribute dimensions.')
			st.write('Graph instance on time point', time_sel, 'and ', attributes_sel, ' attribute.')
			st.write('Number of ', attributes_sel, 'values: ', len(nodes_per_attr_value_dct))
			st.write('Sampling: ', sampling)
			st.write('Number of nodes in the network: ', len(nodes))

			palette = ['#9fbfdf','#ff6633','#79d279','#0f5aa6','#006600','#bf80ff','#264d73','#ffb366','#808000','#c2d6d6',\
						'#ffaa00','#808080','#cccccc','#d46e3b','#ff00ff','#00e600','#ff5050','#8cd9b3','#66ffcc','#802b00',\
						'#194d33','#ffaa00','#664400','#33004d','#660066','#006666','#669999','#bf4080','#73264d','#bbbb77',\
						'#004080','#bf4040','#0077b3']

			nodes_graph = []
			inx = 0
			for key,val in nodes_per_attr_value_dct.items():
				for node in val:
					nodes_graph.append(Node(id=node,
								  #size=15,
								  title=node,
			    				  label=key,
			                      symbolType='dot',
			                      font={'enabled':True,'color':palette[inx]},
			                      physics=False,
			                      color={'border':'black','background':palette[inx]}))
				inx += 1

			edges_graph = []
			for edge in edges:
			        edges_graph.append(
			            Edge(source=edge[0],
			                 target=edge[1], 
			                 smooth= {'enabled':True,'type':'dynamic'},
			                 font={'color':'black'},
			                 #length=300,
			                 color='black')
			        )

			config = Config(width=1000, 
			                height=500,
			                #graphviz_layout='fdp',
			                #graphviz_config={"rankdir": rankdir, "ranksep": ranksep, "nodesep": nodesep},
			                directed=True,
			                enabled=True,
			                #initiallyActive=True,
			                nodeHighlightBehavior=True, 
			                highlightColor="#F7A7A6",
			                collapsible=True,
			                node={'labelProperty':'label'},
			                link={'labelProperty': 'label', 'renderLabel': True},
			                maxZoom=2,
			                minZoom=0.1,
			                staticGraphWithDragAndDrop=False,
			                staticGraph=False,
			                initialZoom=1
			                )

			return_value = agraph(nodes=nodes_graph, 
			                      edges=edges_graph, 
			                      config=config)


# Aggregation
elif app_mode == "Graph Aggregation":
	with st.sidebar:
		#Choose Dataset
		st.title('Dataset')
		dataset = st.selectbox('Choose dataset',['DBLP','MovieLens','Primary School'])
		if dataset == 'DBLP':
			stc = ['Gender']
			varying = ['#Publications']
			edges_df = pd.read_csv('datasets/dblp_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/dblp_dataset/nodes.csv', sep=' ', index_col=0)
			time_variant_attr = pd.read_csv('datasets/dblp_dataset/time_variant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/dblp_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr.rename(columns={'0': 'gender'}, inplace=True)
			nodes_df.index.names = ['userID']
			time_invariant_attr.gender.replace(['female','male'], ['F','M'],inplace=True)
		elif dataset == 'MovieLens':
			stc = ['Gender','Age','Occupation']
			varying = ['Rating']
			edges_df = pd.read_csv('datasets/movielens_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/movielens_dataset//nodes.csv', sep=' ', index_col=0)
			time_variant_attr = pd.read_csv('datasets/movielens_dataset/time_variant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/movielens_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
		elif dataset == 'Primary School':
			stc = ['Gender','Class']
			edges_df = pd.read_csv('datasets/school_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/school_dataset//nodes.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/school_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
			time_variant_attr = []
			varying = []
		period = list(edges_df.columns)

		with st.expander('Load your dataset'):
			uploaded_files = st.file_uploader("Choose a CSV file", type='csv', accept_multiple_files=True)
			for uploaded_file in uploaded_files:
				if uploaded_file.name == 'edges.csv':
					edges_df = pd.read_csv(uploaded_file, sep=' ', index_col=[0,1])
				if uploaded_file.name == 'nodes.csv':
					nodes_df = pd.read_csv(uploaded_file, sep=' ', index_col=0)
				if uploaded_file.name == 'time_variant_attr.csv':
					time_variant_attr = pd.read_csv(uploaded_file, sep=' ', index_col=0)
				if uploaded_file.name == 'time_invariant_attr.csv':
					time_invariant_attr = pd.read_csv(uploaded_file, sep=' ', index_col=0)
		
				period = list(edges_df.columns)
				stc = list(time_invariant_attr.columns)
				varying = ['varying']
	palette = ['#9fbfdf','#ff6633','#79d279','#0f5aa6','#006600','#bf80ff','#264d73','#ffb366','#808000','#c2d6d6',\
			'#ffaa00','#808080','#cccccc','#d46e3b','#ff00ff','#00e600','#ff5050','#8cd9b3','#66ffcc','#802b00',\
			'#194d33','#ffaa00','#664400','#33004d','#660066','#006666','#669999','#bf4080','#73264d','#bbbb77',\
			'#004080','#bf4040','#0077b3']
	with st.sidebar:
		#with st.expander('Set up Aggregation'):
		st.title('Set up Aggregation')
		#col_time_left, col_time_right = st.columns(2)
		#with col_time_left:
			#time_left = st.multiselect("Left Interval", period)

		interval_or_tp = st.selectbox('Time dimension',['Interval','Time Point'])
		if interval_or_tp == 'Interval':
			time_left_start,time_left_stop = st.select_slider("Left Interval", options=period,value=(period[0],period[2]))
			time_left = period[period.index(time_left_start):period.index(time_left_stop)+1]
			time_left = [str(i) for i in time_left]
			st.write('Selected left interval: [', time_left[0], ',', time_left[-1], ']')
			#with col_time_right:
				#time_right = st.multiselect("Right Interval", [i for i in period if i not in time_left])
			time_right_start,time_right_stop = st.select_slider("Right Interval", options=period,value=(period[3],period[5]))
			time_right = period[period.index(time_right_start):period.index(time_right_stop)+1]
			time_right = [str(i) for i in time_right]
			st.write('Selected right interval: [', time_right[0], ',', time_right[-1], ']')
			operator = st.selectbox('Operator',['Union','Intersection','Difference','Evolution'])
			agg_type = st.selectbox('Type',['Non-Distinct','Distinct'])
			timepoint = False

		elif interval_or_tp == 'Time Point':
			timepoint = st.selectbox('Time point',period)
			time_left = False
			time_right = False
			operator = False
			agg_type = False


		attributes = st.multiselect("Attributes", stc+varying)
		submitted = st.button('Aggregate')
		if interval_or_tp == 'Interval':
			if submitted and (not time_left or not time_right or not operator or not attributes or not agg_type):
				st.error('Required fields missing.')#, icon="????")
			elif submitted and time_left and time_right and operator and attributes and agg_type:
				if list(set(time_left).intersection(time_right)):
					st.error('Overlapping intervals.')
		elif interval_or_tp == 'Time Point':
			if submitted and (not timepoint or not attributes):
				st.error('Required fields missing.')#, icon="????")

	with st.container():
		if timepoint and attributes and submitted:
			with st.spinner('Wait for it...'):
				time.sleep(3)

			st.subheader('Aggregation Output')
			#st.subheader('A global view of the graph as filtered by the time operator and grouped on one or more attributes.')
			st.write('Aggregation graph on time point ', timepoint , ' for ', ", ".join(attributes), ' attribute(s).')


			if any(i in stc for i in attributes) and not any(i in varying for i in attributes):
				res, tia = eval('Union_Static')(nodes_df,edges_df,time_invariant_attr,[timepoint])
				agg = eval('Aggregate_Static_Dist')(res,tia,[i.lower() for i in attributes if i not in varying])
				create_Graph(agg,palette,0)
			elif any(i in varying for i in attributes) and not any(i in stc for i in attributes):
				res, tva = eval('Union_Variant')(nodes_df,edges_df,time_variant_attr,[timepoint])
				agg = eval('Aggregate_Variant_All')(res,tva,[timepoint])
				create_Graph(agg,palette,0)
			elif any(i in stc for i in attributes) and any(i in varying for i in attributes):
				res, tia, tva = eval('Union_Mix')(nodes_df,edges_df,time_invariant_attr,time_variant_attr,[timepoint])
				agg = eval('Aggregate_Mix_All')(res,tva,tia,[i.lower() for i in attributes if i not in varying],[timepoint])
				create_Graph(agg,palette,0)
			

		elif time_left and time_right and operator and attributes and agg_type and submitted:
			if not list(set(time_left).intersection(time_right)):
				with st.spinner('Wait for it...'):
				    time.sleep(3)

				st.title('Aggregation Output')
				st.subheader('A global view of the graph as filtered by the time operator and grouped on one or more attributes.')
				st.write(agg_type, 'aggregation ', operator.lower(), 'graph on ', '[', time_left[0], ',', time_left[-1], '], ', '[', time_right[0], ',', time_right[-1], ']', ' intervals for ', ", ".join(attributes), ' attribute(s).')

				settings = {}
				if operator == 'Difference':
					settings['operator'] = 'Diff'
				else:
					settings['operator'] = operator
				if agg_type == 'Non-Distinct':
					settings['type'] = 'All'
				elif agg_type == 'Distinct':
					settings['type'] = 'Dist'
				settings['left'] = time_left
				settings['right'] = time_right
				settings['left'] = [i.lower() for i in settings['left']]
				settings['right'] = [i.lower() for i in settings['right']]
				settings['static'] = [i.lower() for i in attributes if i not in varying]

				if settings['operator'] == 'Union' or settings['operator'] == 'Intersection':
					interval = settings['left']+settings['right']
					if any(i in stc for i in attributes) and not any(i in varying for i in attributes):
						res, tia = eval(settings['operator'] + '_Static')(nodes_df,edges_df,time_invariant_attr,interval)
						agg = eval('Aggregate_Static_' + settings['type'])(res,tia,settings['static'])
					elif any(i in varying for i in attributes) and not any(i in stc for i in attributes):
						res, tva = eval(settings['operator'] + '_Variant')(nodes_df,edges_df,time_variant_attr,interval)
						agg = eval('Aggregate_Variant_' + settings['type'])(res,tva,interval)
					elif any(i in stc for i in attributes) and any(i in varying for i in attributes):
						res, tia, tva = eval(settings['operator'] + '_Mix')(nodes_df,edges_df,time_invariant_attr,time_variant_attr,interval)
						agg = eval('Aggregate_Mix_' + settings['type'])(res,tva,tia,settings['static'],interval)

					try:
						create_Graph(agg,palette,0)
					except:
						st.write('There is no', operator.lower(), 'aggregate graph for the specified intervals', ':neutral_face:')

				elif settings['operator'] == 'Diff':
					interval_diffL = settings['left']
					interval_diffR = settings['right']
					if any(i in stc for i in attributes) and not any(i in varying for i in attributes):
						res, tia = eval(settings['operator'] + '_Static')(nodes_df,edges_df,time_invariant_attr,interval_diffL,interval_diffR)
						agg_tmp = eval('Aggregate_Static_' + settings['type'])(res,tia,settings['static'])
						agg = eval(settings['operator'] + '_Post_Agg_Static')(agg_tmp,settings['static'])
					elif any(i in varying for i in attributes) and not any(i in stc for i in attributes):
						res, tva = eval(settings['operator'] + '_Variant')(nodes_df,edges_df,time_variant_attr,interval_diffL,interval_diffR)
						agg_tmp = eval('Aggregate_Variant_' + settings['type'])(res,tva,interval_diffL)
						agg = eval(settings['operator'] + '_Post_Agg_Variant')(agg_tmp)
					elif any(i in stc for i in attributes) and any(i in varying for i in attributes):
						res, tia, tva = eval(settings['operator'] + '_Mix')(nodes_df,edges_df,time_invariant_attr,time_variant_attr,interval_diffL,interval_diffR)
						agg_tmp = eval('Aggregate_Mix_' + settings['type'])(res,tva,tia,settings['static'],interval_diffL)
						agg = eval(settings['operator'] + '_Post_Agg_Mix')(agg_tmp,settings['static'])

					try:
						create_Graph(agg,palette,0)
					except:
						st.write('There is no', operator.lower(), 'aggregate graph for the specified intervals', ':neutral_face:')

				elif settings['operator'] == 'Evolution':
					interval = settings['left']+settings['right']
					interval_diffL = settings['left']
					interval_diffR = settings['right']	
					if any(i in stc for i in attributes) and not any(i in varying for i in attributes):
						res, tia = eval('Intersection_Static')(nodes_df,edges_df,time_invariant_attr,interval)
						agg_stable = eval('Aggregate_Static_' + settings['type'])(res,tia,settings['static'])
						res, tia = eval('Diff_Static')(nodes_df,edges_df,time_invariant_attr,interval_diffL,interval_diffR)
						agg_tmp = eval('Aggregate_Static_' + settings['type'])(res,tia,settings['static'])
						agg_del = eval('Diff_Post_Agg_Static')(agg_tmp,settings['static'])
						res, tia = eval('Diff_Static')(nodes_df,edges_df,time_invariant_attr,interval_diffR,interval_diffL)
						agg_tmp = eval('Aggregate_Static_' + settings['type'])(res,tia,settings['static'])
						agg_new = eval('Diff_Post_Agg_Static')(agg_tmp,settings['static'])
					elif any(i in varying for i in attributes) and not any(i in stc for i in attributes):
						res, tva = eval('Intersection_Variant')(nodes_df,edges_df,time_variant_attr,interval)
						agg_stable = eval('Aggregate_Variant_' + settings['type'])(res,tva,interval)
						res, tva = eval('Diff_Variant')(nodes_df,edges_df,time_variant_attr,interval_diffL,interval_diffR)
						agg_tmp = eval('Aggregate_Variant_' + settings['type'])(res,tva,interval_diffL)
						agg_del = eval('Diff_Post_Agg_Variant')(agg_tmp)
						res, tva = eval('Diff_Variant')(nodes_df,edges_df,time_variant_attr,interval_diffR,interval_diffL)
						agg_tmp = eval('Aggregate_Variant_' + settings['type'])(res,tva,interval_diffR)
						agg_new = eval('Diff_Post_Agg_Variant')(agg_tmp)
					elif any(i in stc for i in attributes) and any(i in varying for i in attributes):
						res, tia, tva = eval('Intersection_Mix')(nodes_df,edges_df,time_invariant_attr,time_variant_attr,interval)
						agg_stable = eval('Aggregate_Mix_' + settings['type'])(res,tva,tia,settings['static'],interval)
						res, tia, tva = eval('Diff_Mix')(nodes_df,edges_df,time_invariant_attr,time_variant_attr,interval_diffL,interval_diffR)
						agg_tmp = eval('Aggregate_Mix_' + settings['type'])(res,tva,tia,settings['static'],interval_diffL)
						agg_del = eval('Diff_Post_Agg_Mix')(agg_tmp,settings['static'])
						res, tia, tva = eval('Diff_Mix')(nodes_df,edges_df,time_invariant_attr,time_variant_attr,interval_diffR,interval_diffL)
						agg_tmp = eval('Aggregate_Mix_' + settings['type'])(res,tva,tia,settings['static'],interval_diffR)
						agg_new = eval('Diff_Post_Agg_Mix')(agg_tmp,settings['static'])

					agg_list = [agg_stable,agg_del,agg_new]

					tab1,tab2,tab3 = st.tabs(['Stable','Deleted','New'])
					with tab1:
						try:
							create_Graph(agg_list[0],palette,0)
						except:
							st.write('There is no stable aggregate graph for the specified intervals', ':neutral_face:')
					with tab2:
						try:
							create_Graph(agg_list[1],palette,1)
						except:
							st.write('There is no deleted aggregate graph for the specified intervals', ':neutral_face:')
					with tab3:
						try:
							create_Graph(agg_list[2],palette,2)
						except:
							st.write('There is no new aggregate graph for the specified intervals', ':neutral_face:')


# Exploration
elif app_mode == "Graph Exploration":
	with st.sidebar:
		#Choose Dataset
		st.title('Dataset')
		dataset = st.selectbox('Choose dataset',['DBLP','MovieLens','Primary School'])
		if dataset == 'DBLP':
			stc = ['Gender']
			varying = ['#Publications']
			edges_df = pd.read_csv('datasets/dblp_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/dblp_dataset/nodes.csv', sep=' ', index_col=0)
			time_variant_attr = pd.read_csv('datasets/dblp_dataset/time_variant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/dblp_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr.rename(columns={'0': 'gender'}, inplace=True)
			nodes_df.index.names = ['userID']
			time_invariant_attr.gender.replace(['female','male'], ['F','M'],inplace=True)
		elif dataset == 'MovieLens':
			stc = ['Gender','Age','Occupation']
			varying = ['Rating']
			edges_df = pd.read_csv('datasets/movielens_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/movielens_dataset//nodes.csv', sep=' ', index_col=0)
			time_variant_attr = pd.read_csv('datasets/movielens_dataset/time_variant_attr.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/movielens_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
		elif dataset == 'Primary School':
			stc = ['Gender','Class']
			edges_df = pd.read_csv('datasets/school_dataset/edges.csv', sep=' ', index_col=[0,1])
			nodes_df = pd.read_csv('datasets/school_dataset//nodes.csv', sep=' ', index_col=0)
			time_invariant_attr = pd.read_csv('datasets/school_dataset/time_invariant_attr.csv', sep=' ', index_col=0)
			time_variant_attr = []
			varying = []
		period = list(edges_df.columns)

		with st.expander('Load your dataset'):
			uploaded_files = st.file_uploader("Choose a CSV file", type='csv', accept_multiple_files=True)
			for uploaded_file in uploaded_files:
				if uploaded_file.name == 'edges.csv':
					edges_df = pd.read_csv(uploaded_file, sep=' ', index_col=[0,1])
				if uploaded_file.name == 'nodes.csv':
					nodes_df = pd.read_csv(uploaded_file, sep=' ', index_col=0)
				if uploaded_file.name == 'time_variant_attr.csv':
					time_variant_attr = pd.read_csv(uploaded_file, sep=' ', index_col=0)
				if uploaded_file.name == 'time_invariant_attr.csv':
					time_invariant_attr = pd.read_csv(uploaded_file, sep=' ', index_col=0)
		
				period = list(edges_df.columns)
				stc = list(time_invariant_attr.columns)
				varying = ['varying']
	palette = ['#9fbfdf','#ff6633','#79d279','#0f5aa6','#006600','#bf80ff','#264d73','#ffb366','#808000','#c2d6d6',\
			'#ffaa00','#808080','#cccccc','#d46e3b','#ff00ff','#00e600','#ff5050','#8cd9b3','#66ffcc','#802b00',\
			'#194d33','#ffaa00','#664400','#33004d','#660066','#006666','#669999','#bf4080','#73264d','#bbbb77',\
			'#004080','#bf4040','#0077b3']
	submitted_expl = []
	#k_limits = [0]
	with st.sidebar:
		st.title('Set up Exploration')
		event = st.selectbox('Event',['Stability','Growth','Shrinkage'])
		if not isinstance(time_variant_attr,list):
			var_domain = sorted(list(np.unique(time_variant_attr.values.flatten())))
		stc_domain = sorted(list(np.unique(time_invariant_attr.values.flatten())))

		attributes_expl = st.multiselect("Attributes", stc+varying, key='attr_expl')
		stc_attrs = []
		var_attrs = []
		for i in attributes_expl:
			if i in stc:
				stc_attrs.append(i)
			else:
				var_attrs.append(i)

		if stc_attrs and not var_attrs:
			attrtype = 'Static'
		elif not stc_attrs and var_attrs:
			attrtype = 'Variant'
		elif stc_attrs and var_attrs:
			attrtype = 'Mix'

		if attributes_expl:
			st.markdown(f'<p style="color:#373737;font-size:14px;">{"Edge attributes"}</p>', unsafe_allow_html=True)
		col1,col2 = st.columns(2)
		with col1:
			with st.expander('Start Node Value(s)'):
				start_node = []
				if var_attrs:
					start_val = st.selectbox(var_attrs[0], sorted([j for j in list(np.unique(time_variant_attr.values.flatten())) if j!=0]), key=i+'str_2')
					start_val = float(start_val)
					start_node.append(start_val)
				if stc_attrs:
					for i in stc_attrs:
						start_val = st.selectbox(i, sorted(list(np.unique(time_invariant_attr[i.lower()].values.flatten()))), key=i+'str')
						start_node.append(start_val)
		with col2:
			with st.expander('End Node Value(s)'):
				end_node = []
				if var_attrs:
					end_val = st.selectbox(var_attrs[0], sorted([i for i in list(np.unique(time_variant_attr.values.flatten())) if i!=0]), key=i+'stp_2')
					end_val = float(end_val)
					end_node.append(end_val)
				if stc_attrs:
					for i in stc_attrs:
						end_val = st.selectbox(i, sorted(list(np.unique(time_invariant_attr[i.lower()].values.flatten()))), key=i+'stp')
						end_node.append(end_val)

		attr_values = tuple(start_node+end_node)
		stc_attrs = [i.lower() for i in stc_attrs]
		period_expl = [i.lower() for i in period]

		# Set limits
		if attributes_expl and attr_values:
			intvl_pairs = [[i,period_expl[period_expl.index(i)+1]] for i in period_expl[:-1]]
			# Stability limits
			if event == 'Stability':
			    inx_pairs = []
			    if attrtype == 'Static':
				    for i in intvl_pairs:
				        inx,tia_inx = Intersection_Static(nodes_df,edges_df,time_invariant_attr,i)
				        agg_inx = Aggregate_Static_Dist(inx,tia_inx,stc_attrs)
				        try:
				        	inx_pairs.append(agg_inx[1].loc[attr_values][0])
				        except:
				        	continue
			    elif attrtype == 'Variant':
			    	for i in intvl_pairs:
				        inx,tva_inx = Intersection_Variant(nodes_df,edges_df,time_variant_attr,i)
				        agg_inx = Aggregate_Variant_Dist(inx,tva_inx,i)
				        try:
				        	inx_pairs.append(agg_inx[1].loc[attr_values][0])
				        except:
				        	continue
			    elif attrtype == 'Mix':
			    	for i in intvl_pairs:
				        inx,tia_inx,tva_inx = Intersection_Mix(nodes_df,edges_df,time_invariant_attr,time_variant_attr,i)
				        agg_inx = Aggregate_Mix_Dist(inx,tva_inx,tia_inx,stc_attrs,i)
				        try:
				        	inx_pairs.append(agg_inx[1].loc[attr_values][0])
				        except:
				        	continue
			# Growth limits
			elif event == 'Growth':
				diff_pairs_G = []
				if attrtype == 'Static':
					for i in intvl_pairs:
						diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,[i[1]],[i[0]])
						agg_diff_G = Aggregate_Static_Dist(diff,tia_diff,stc_attrs)
						try:
							diff_pairs_G.append(agg_diff_G[1].loc[attr_values][0])
						except:
							continue
				elif attrtype == 'Variant':
					for i in intvl_pairs:
						diff,tva_diff = Diff_Variant(nodes_df,edges_df,time_variant_attr,[i[1]],[i[0]])
						agg_diff_G = Aggregate_Variant_Dist(diff,tva_diff,[i[1]])
						try:
							diff_pairs_G.append(agg_diff_G[1].loc[attr_values][0])
						except:
							continue
				elif attrtype == 'Mix':
					for i in intvl_pairs:
						diff,tia_diff,tva_diff = Diff_Mix(nodes_df,edges_df,time_invariant_attr,time_variant_attr,[i[1]],[i[0]])
						agg_diff_G = Aggregate_Mix_Dist(diff,tva_diff,tia_diff,stc_attrs,[i[1]])
						try:
							diff_pairs_G.append(agg_diff_G[1].loc[attr_values][0])
						except:
							continue
			# Shrinkage limits
			elif event == 'Shrinkage':
				diff_pairs_S = []
				if attrtype == 'Static':
					for i in intvl_pairs:
						diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,[i[0]],[i[1]])
						agg_diff_S = Aggregate_Static_Dist(diff,tia_diff,stc_attrs)
						try:
							diff_pairs_S.append(agg_diff_S[1].loc[attr_values][0])
						except:
							continue
					diff,tia_diff = Diff_Static(nodes_df,edges_df,time_invariant_attr,i[:-1],[i[-1]])
					agg_diff_S = Aggregate_Static_Dist(diff,tia_diff,stc_attrs)
					try:
						shrinkage_max = agg_diff_S[1].loc[attr_values][0]
					except:
						pass
				elif attrtype == 'Variant':
					for i in intvl_pairs:
						diff,tva_diff = Diff_Variant(nodes_df,edges_df,time_variant_attr,[i[0]],[i[1]])
						agg_diff_S = Aggregate_Variant_Dist(diff,tva_diff,[i[0]])
						try:
							diff_pairs_S.append(agg_diff_S[1].loc[attr_values][0])
						except:
							continue
					diff,tva_diff = Diff_Variant(nodes_df,edges_df,time_variant_attr,i[:-1],[i[-1]])
					agg_diff_S = Aggregate_Variant_Dist(diff,tva_diff,i[:-1])
					try:
						shrinkage_max = agg_diff_S[1].loc[attr_values][0]
					except:
						pass
				elif attrtype == 'Mix':
					for i in intvl_pairs:
						diff,tia_diff,tva_diff = Diff_Mix(nodes_df,edges_df,time_invariant_attr,time_variant_attr,[i[0]],[i[1]])
						agg_diff_S = Aggregate_Mix_Dist(diff,tva_diff,tia_diff,stc_attrs,[i[0]])
						try:
							diff_pairs_S.append(agg_diff_S[1].loc[attr_values][0])
						except:
							continue
					diff,tia_diff,tva_diff = Diff_Mix(nodes_df,edges_df,time_invariant_attr,time_variant_attr,i[:-1],[i[-1]])
					agg_diff_S = Aggregate_Mix_Dist(diff,tva_diff,tia_diff,stc_attrs,i[:-1])
					try:
						shrinkage_max = agg_diff_S[1].loc[attr_values][0]
					except:
						pass
			#try:
			if event == 'Stability':
				if inx_pairs:
					k_limits = [1,int(max(inx_pairs))]
				else:
					st.error('Invalid attribute values.')
					k_limits = [0]
			elif event == 'Growth':
				if diff_pairs_G:
					k_limits = [int(min(diff_pairs_G)),int(max(diff_pairs_G))]
				else:
					st.error('Invalid attribute values.')
					k_limits = [0]
			elif event == 'Shrinkage':
				if diff_pairs_S:
					k_limits = [int(min(diff_pairs_S)),shrinkage_max]
				else:
					st.error('Invalid attribute values.')
					k_limits = [0]
			if k_limits != [0]:
				#k = st.number_input('Number of interactions', min_value=k_limits[0], max_value=k_limits[-1])
				if k_limits[0] != k_limits[1]:
					k = st.slider('Number of interactions', min_value=k_limits[0], max_value=k_limits[-1])
					st.write('The current number is ', int(k))
				else:
					k=k_limits[0]
					st.write('There is only', k_limits[0], 'interaction to explore.')
				submitted_expl = st.button('Explore')
				if submitted_expl:
					if attrtype=='Static':
						if event == 'Stability':
							result,myagg = Stability_Intersection_Static_a(k,period_expl,nodes_df,edges_df,time_invariant_attr,stc_attrs,attr_values)
							result = result[::-1]
						elif event == 'Growth':
							result,myagg = Growth_Union_Static_a(k,period_expl,nodes_df,edges_df,time_invariant_attr,stc_attrs,attr_values)
							result = result[::-1]
						elif event == 'Shrinkage':
							result,myagg = Shrink_Union_Static_a(k,period_expl,nodes_df,edges_df,time_invariant_attr,stc_attrs,attr_values)
							result = result[::-1]
					elif attrtype=='Variant':
						if event == 'Stability':
							result,myagg = Stability_Intersection_Variant_a(k,period_expl,nodes_df,edges_df,time_variant_attr,attr_values)
							result = result[::-1]
						elif event == 'Growth':
							result,myagg = Growth_Union_Variant_a(k,period_expl,nodes_df,edges_df,time_variant_attr,attr_values)
							result = result[::-1]
						elif event == 'Shrinkage':
							result,myagg = Shrink_Union_Variant_a(k,period_expl,nodes_df,edges_df,time_variant_attr,attr_values)
							result = result[::-1]
					elif attrtype=='Mix':
						if event == 'Stability':
							result,myagg = Stability_Intersection_Mix_a(k,period_expl,nodes_df,edges_df,time_invariant_attr,time_variant_attr,stc_attrs,attr_values)
							result = result[::-1]
						elif event == 'Growth':
							result,myagg = Growth_Union_Mix_a(k,period_expl,nodes_df,edges_df,time_invariant_attr,time_variant_attr,stc_attrs,attr_values)
							result = result[::-1]
						elif event == 'Shrinkage':
							result,myagg = Shrink_Union_Mix_a(k,period_expl,nodes_df,edges_df,time_invariant_attr,time_variant_attr,stc_attrs,attr_values)
							result = result[::-1]


					result_lst = []
					for lst in result:
						for i in lst[0]:
							tmp = [i,lst[1][0]]
							result_lst.append(tmp)

					# map str to num
					str_num = {}
					for i in range(len(period_expl)):
						str_num[period_expl[i]] = i

					# map num to str
					num_str = {}
					for i in range(len(period_expl)):
						num_str[i] = period_expl[i]

					# convert time points to strings
					result_lst = [[str_num[i],str_num[j]] for i,j in result_lst]

					result_df = pd.DataFrame(result_lst)
					df_cols = ['Interval','Point of Reference']
					result_df.columns = df_cols
					result_df_grouped = [i[1].values.tolist() for i in result_df.groupby('Point of Reference')]
					#result_df_grouped = [[i[0],i[-1]] if len(i)>2 else i for i in result_df_grouped]
					result_df_grouped = [[i[0],i[-1]] for i in result_df_grouped]
					result_df_grouped = [i for sublst in result_df_grouped for i in sublst]
					# # return to str
					result_df = pd.DataFrame(result_df_grouped)
					result_df.columns = df_cols
					
					x = result_df['Interval'].tolist()
					#x_str = [num_str[i].upper() for i in x]
					y = result_df['Point of Reference'].tolist()
					#y_str = [num_str[i].upper() for i in y]
					fig = px.line(result_df, x="Interval", y="Point of Reference", color='Point of Reference', markers=True)
					fig.update_traces(textposition="bottom right", marker_size=12, line=dict(width=2.5), line_color="#4169E1")
					fig.update_layout(
					    xaxis = dict(
					        tickmode = 'array',
					        # tickvals = x,
					        # ticktext = x_str
					        tickvals = [i for i in range(len(period_expl))],
					        ticktext = [i.upper() for i in period_expl]
					    ),
					    yaxis = dict(
					        tickmode = 'array',
					        # tickvals = y,
					        # ticktext = y_str
					        tickvals = [i for i in range(len(period_expl))],
					        ticktext = [i.upper() for i in period_expl]
					    ),
					    showlegend=False, font_size=20, width=750, height=600
					)
					
				# #fig.update_traces(textposition="bottom right", line_color="#6666ff", marker_size=15)
				# #fig.show()


	if submitted_expl and attributes_expl:
		with st.container():
			#try:
			if submitted_expl and result_lst:
				with st.spinner('Wait for it...'):
					time.sleep(3)
				st.subheader('Exploration Output')
				#st.subheader('Points in graph where at least _k_ interactions of a type have occured compared to appropriate past intervals.')
				attr_values = tuple([str(i) for i in attr_values])
				st.write('Derived intervals on ', event.lower(), ' _event_ for at least ', k, 'interaction(s) and edge type: ((', ", ".join(attr_values[:int(len(attr_values)/2)]), '), ', '(', ", ".join(attr_values[int(len(attr_values)/2):]), ')).')
				#st.write(attr_values)
				st.plotly_chart(fig, use_container_width=True)
			#except:
			elif submitted_expl and not result_lst:
				st.title('Exploration Output')
				st.write('There are no results for ', int(k), 'interaction(s) ', ':neutral_face:')
