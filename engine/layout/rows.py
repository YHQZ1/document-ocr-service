def cluster_rows(tokens, y_threshold=0.01):
    tokens_sorted = sorted(tokens, key=lambda t: t["y"])

    rows = []
    current_row = []
    current_y = None

    for token in tokens_sorted:
        if current_y is None:
            current_row.append(token)
            current_y = token["y"]
            continue

        if abs(token["y"] - current_y) <= y_threshold:
            current_row.append(token)
        else:
            rows.append(current_row)
            current_row = [token]
            current_y = token["y"]

    if current_row:
        rows.append(current_row)

    for row in rows:
        row.sort(key=lambda t: t["x"])

    return rows