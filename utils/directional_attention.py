import torch
import torch.nn.functional as F

def bounding_box_to_center(input_tensor):
    """
    Convert bounding box coordinates to center point positions.
    
    Args:
    - input_tensor (torch.Tensor): Tensor of shape (num_frame, num_node, 4)
      where each 4-vector represents the bounding box [x_min, y_min, x_max, y_max]
    
    Returns:
    - center_points (torch.Tensor): Tensor of shape (num_frame, num_node, 2)
      where each 2-vector represents the center point [x_center, y_center]
    """
    
    # Extract bounding box coordinates
    x_min = input_tensor[:, :, 0]
    y_min = input_tensor[:, :, 1]
    x_width = input_tensor[:, :, 2]
    y_height = input_tensor[:, :, 3]
    
    # Compute center point positions
    x_center = x_min + x_width / 2
    y_center = y_min + y_height / 2
    
    # Combine x_center and y_center into a single tensor
    center_points = torch.stack([x_center, y_center], dim=-1)
    
    return center_points


def calculate_attention_scores(input_tensor):
    """
    Calculate the attention scores based on directional cosine similarity.

    Parameters:
    - input_tensor: numpy array of shape (num_frame, num_node, node_feature)
      where node_feature is the bounding box coordinates of the object.

    Returns:
    - attention_map: numpy array of shape (num_frame, num_node, num_node)
    """
    # Initialize variables
    num_frame, num_node, _ = input_tensor.shape
    attention_map = torch.zeros((num_frame, num_node, num_node)).to(input_tensor.device)

    center_points = bounding_box_to_center(input_tensor)
    
    for t in range(1, num_frame):  # Starting from 1 because we need t-1
        for i in range(num_node):
            # Calculate velocity for node i at frame t
            velocity_i = center_points[t, i, :] - center_points[t-1, i, :]
            
            for j in range(num_node):
                # Calculate velocity for node j at frame t
                velocity_j = center_points[t, j, :] - center_points[t-1, j, :]
                
                # Calculate the norms
                norm_i = torch.linalg.norm(velocity_i)
                norm_j = torch.linalg.norm(velocity_j)
                
                # If norms are zero, the cosine similarity is undefined. 
                # In this case, set the similarity to 0.
                if norm_i == 0 or norm_j == 0:
                    cosine_similarity = 0
                else:
                    # Calculate cosine similarity
                    cosine_similarity = torch.dot(velocity_i, velocity_j) / (norm_i * norm_j)
                
                attention_map[t, i, j] = cosine_similarity
                
        # Apply softmax to the attention scores for each node at frame t
        attention_map[t, :, :] = torch.softmax(attention_map[t, :, :], axis=1)
    
    return attention_map

