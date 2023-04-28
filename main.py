from kmeans.kmeans import *
from cvrptw.cvrptw import *
import pandas as pd
import os
import multiprocessing

if __name__ == '__main__':
    stop = pd.read_excel('stoppoint.xlsx')  # Đọc dữ liệu khách hàng
    depot = pd.read_excel('depot.xlsx')  # Đọc dữ liệu kho
    kmeans(stop, depot)

    processes = []
    for depot_file_name in os.listdir("depot"):
        process = multiprocessing.Process(target=cvrptw, args=(depot_file_name,))
        processes.append(process)
        process.start()


    # process = multiprocessing.Process(target=cvrptw, args=("depot_2",))
    # processes.append(process)
    # process.start()


    for process in processes:
        process.join()

