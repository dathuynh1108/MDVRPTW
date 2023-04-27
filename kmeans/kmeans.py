import pandas as pd
import numpy as np
import os

def kmeans(stop, depot):
    count_stop = stop.shape[0]  # số khách hàng
    count_row = depot.shape[0]  # số kho

    def process_depot_data(depot_index, depot_data):
        dir = os.path.join("depot", "depot_" + str(depot_index+1))
        if not os.path.exists(dir):
            os.mkdir(dir)
        depot_file_path_txt = os.path.join(dir, "depot_" + str(depot_index+1) + ".txt")
        depot_file_path_excel = os.path.join(dir, "depot_" + str(depot_index+1) + ".xlsx")
        with open(depot_file_path_txt, "w", encoding="utf-8") as f:
            # Thêm kho vô hàng đầu
            depot_row = pd.DataFrame({
                "X": [depot.iloc[depot_index]["X"]],
                "Y": [depot.iloc[depot_index]["Y"]],
                "DEMAND": [0],
                "START": [depot.iloc[depot_index]["START"]],
                "END": [depot.iloc[depot_index]["END"]],
                "SERVICE TIME": [0],
            })
            depot_data = pd.concat([depot_row, depot_data])
            # print
            depot_data.drop(columns=["CLOSEST"], inplace=True, axis=1)
            depot_data.reset_index(drop=True, inplace=True)

            f.write("VEHICLE\n")
            f.write("NUMBER     CAPACITY\n")
            f.write("  50          100\n")
            f.write("\nCUSTOMER\n")
            f.write(depot_data.to_string())
        depot_data.to_excel(depot_file_path_excel, index=False)  
    
    # K-MEANS CLUSTERING
    centroids = {i+1: [depot.loc[i, 'X'], depot.loc[i, 'Y'],
                       depot.loc[i, 'START'], depot.loc[i, 'END']] for i in range(count_row)}

    # Tính khoảng cách xấp xỉ giữa khách hàng với kho
    for i in centroids.keys():
        stop['DISTANCE_FROM_{}'.format(i)] = (
            np.sqrt(
                (stop['X'] - centroids[i][0]) ** 2
                + (stop['Y'] - centroids[i][1]) ** 2
            )
        )
    centroid_distance_cols = [
        'DISTANCE_FROM_{}'.format(i) for i in centroids.keys()]
    stop['CLOSEST'] = stop.loc[:, centroid_distance_cols].idxmin(axis=1)
    # Phân nhóm các khách hàng về từng kho
    group = stop[['NAME', 'ADDRESS', 'X', 'Y', 'DEMAND', 'START',
                  'END', 'SERVICE TIME', 'CLOSEST']]

    # group = stop[['X','Y','start','end','closest','address']]
    g = pd.DataFrame()
    for i in range(count_row):
        group_by_depot = group[group['CLOSEST'] == 'DISTANCE_FROM_' + str(i+1)]
        process_depot_data(i, group_by_depot.copy())
        g = pd.concat([g, group_by_depot])

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(g.to_string())
