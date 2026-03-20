def build_row_column_matrix(rows):
    matrix = []

    for row in rows:
        row_dict = {}

        for token in row:
            col = token["col_id"]

            if col not in row_dict:
                row_dict[col] = []

            row_dict[col].append(token)

        matrix.append(row_dict)

    return matrix