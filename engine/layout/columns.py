import numpy as np

def infer_column_centers(tokens, x_threshold=0.03):
    xs = sorted([t["x"] for t in tokens])

    clusters = []
    current_cluster = [xs[0]]

    for x in xs[1:]:
        if abs(x - np.mean(current_cluster)) <= x_threshold:
            current_cluster.append(x)
        else:
            clusters.append(current_cluster)
            current_cluster = [x]

    clusters.append(current_cluster)

    centers = [float(np.mean(cluster)) for cluster in clusters]

    return centers
  
def assign_columns(tokens, column_centers):
    for token in tokens:
        distances = [abs(token["x"] - c) for c in column_centers]
        token["col_id"] = int(np.argmin(distances))

    return tokens