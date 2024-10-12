import torch
import torch.nn as nn
import network_current
import MyGraph
import graph_generator
import os
import torch.optim as optim
import json



if __name__ == '__main__':
    num_nodes = 52
    seed = 42
    root_path = './annotations/'
    
    train_file_folder = os.listdir(root_path + 'train')
    train_features = []
    train_edge_indices = []
    train_lh_labels = []
    train_rh_labels = []

    train_data = {}
    test_data = {}

    train_lh_label = {}
    train_rh_label = {}
    test_lh_label = {}
    test_rh_label = {}
    
    for train_file in train_file_folder:
        annotation_file = root_path + 'train/' + train_file +'/annoations.json'
        generated_graph = graph_generator.GraphGenerator(annotation_file, num_nodes, seed)
        num_timesteps = generated_graph.get_video_length()
        class_feature_map = generated_graph.get_class_feature_map()
        location_feature_map = generated_graph.get_location_feature_map()
        appearance_feature_map = generated_graph.get_appearance_feature_map()
        edge_feature_map = generated_graph.get_edge_feature_map()

        graph = MyGraph.MotionGraph(num_nodes, class_feature_map, location_feature_map, appearance_feature_map, num_timesteps, seed, edge_feature_map)

        hand_node = [48, 49]
        # Add nodes and edges, here we only add edges between hands and other objects
        for i in range(num_nodes):
            graph.add_node(i)
            if i in hand_node:
                for j in range(num_nodes):
                    if i != j:
                        for t in range(num_timesteps):
                            graph.add_edge(i, j, t)
            else:
                continue

        node_feature_map = graph.get_location_feature_map()  # size: [num_timesteps, 51, 128]   
        adjacency_matrix = graph.get_adjacency_matrix()  # size: [num_timesteps, 51, 51]
        edge_feature_map = graph.get_edge_feature_map()  # size: [50, 10, 10, 128]

        edge_indices = []  # size: [2, num_edges]
        for frame in range(adjacency_matrix.shape[0]):
            edge_index_frame = adjacency_matrix[frame].nonzero().t()
            edge_indices.append(edge_index_frame.unsqueeze(0))
        edge_indices = torch.cat(edge_indices,dim=0)  # size: [num_timesteps, 2, num_edges]

        train_features.append(node_feature_map)
        train_edge_indices.append(edge_indices)

        lh_label_path = root_path + 'train/' + train_file + '/labels/lh_pt.txt'
        rh_label_path = root_path + 'train/' + train_file + '/labels/lh_pt.txt'
        lh_label = []
        rh_label = []

        with open(lh_label_path,'r') as f:
            for line in f:
                lh_label.append(int(line.strip()))
        lh_label = torch.tensor(lh_label)

        with open(rh_label_path,'r') as f:
            for line in f:
                rh_label.append(int(line.strip()))
        rh_label = torch.tensor(rh_label)

        train_lh_labels.append(lh_label)
        train_rh_labels.append(rh_label)
    
    train_lh_label['labels'] = train_lh_labels
    with open('./train_lh_labels.json','w') as f:
        json.dump(train_lh_label, f, indent=4)
    
    train_rh_label['labels'] = train_rh_labels
    with open('./train_rh_labels.json','w') as f:
        json.dump(train_rh_label, f, indent=4)
    
    train_data['node_feature'] = train_features
    train_data['edge_indices'] = train_edge_indices
    with open('./train_data.json','w') as f:
        json.dump(train_data, f, indent=4)
    
    

    test_file_folder = os.listdir(root_path + 'test')
    test_features = []
    test_edge_indices = []
    test_lh_labels = []
    test_rh_labels = []
    
    for test_file in test_file_folder:
        annotation_file = root_path + 'test/' + test_file +'/annoations.json'
        generated_graph = graph_generator.GraphGenerator(annotation_file, num_nodes, seed)
        num_timesteps = generated_graph.get_video_length()
        class_feature_map = generated_graph.get_class_feature_map()
        location_feature_map = generated_graph.get_location_feature_map()
        appearance_feature_map = generated_graph.get_appearance_feature_map()
        edge_feature_map = generated_graph.get_edge_feature_map()

        graph = MyGraph.MotionGraph(num_nodes, class_feature_map, location_feature_map, appearance_feature_map, num_timesteps, seed, edge_feature_map)

        hand_node = [49, 50]
        # Add nodes and edges, here we only add edges between hands and other objects
        for i in range(num_nodes):
            graph.add_node(i)
            if i in hand_node:
                for j in range(num_nodes):
                    if i != j:
                        for t in range(num_timesteps):
                            graph.add_edge(i, j, t)
            else:
                continue

        node_feature_map = graph.get_location_feature_map()  # size: [num_timesteps, 51, 128]   
        adjacency_matrix = graph.get_adjacency_matrix()  # size: [num_timesteps, 51, 51]
        edge_feature_map = graph.get_edge_feature_map()  # size: [50, 10, 10, 128]

        edge_indices = []  # size: [2, num_edges]
        for frame in range(adjacency_matrix.shape[0]):
            edge_index_frame = adjacency_matrix[frame].nonzero().t()
            edge_indices.append(edge_index_frame.unsqueeze(0))
        edge_indices = torch.cat(edge_indices,dim=0)  # size: [num_timesteps, 2, num_edges]

        test_features.append(node_feature_map)
        test_edge_indices.append(edge_indices)

        lh_label_path = root_path + 'test/' + test_file + '/labels/lh_pt.txt'
        rh_label_path = root_path + 'test/' + test_file + '/labels/lh_pt.txt'
        lh_label = []
        rh_label = []

        with open(lh_label_path,'r') as f:
            for line in f:
                lh_label.append(int(line.strip()))
        lh_label = torch.tensor(lh_label)

        with open(rh_label_path,'r') as f:
            for line in f:
                rh_label.append(int(line.strip()))
        rh_label = torch.tensor(rh_label)

        test_lh_labels.append(lh_label)
        test_rh_labels.append(rh_label)

    test_lh_label['labels'] = test_lh_labels
    with open('./test_lh_labels.json','w') as f:
        json.dump(test_lh_label, f, indent=4)
    
    test_rh_label['labels'] = test_rh_labels
    with open('./test_rh_labels.json','w') as f:
        json.dump(test_rh_label, f, indent=4)
    
    test_data['node_feature'] = test_features
    test_data['edge_indices'] = test_edge_indices
    with open('./test_data.json','w') as f:
        json.dump(test_data, f, indent=4)

    
     