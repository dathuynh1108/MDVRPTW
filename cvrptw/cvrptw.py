from .instance_loader3 import *
import os
from .simulated_annealing import sa_algorithm
from .draw import *
import matplotlib.pyplot as plt
import time

def cvrptw(instance_name):
    cwd = os.getcwd()
    depot_dir = os.path.join(cwd, "depot", instance_name)
    result_filepath = os.path.join(cwd, "result", instance_name + ".txt")
    print("Start to run", instance_name)
    f = open(result_filepath, "w", encoding="utf-8")

    filepath_txt = os.path.join(depot_dir, instance_name + ".txt")   
    filepath_xlsx = os.path.join(depot_dir, instance_name + ".xlsx")
    instance = load_from_file(filepath_txt, filepath_xlsx)
    instance.find_initial_solution()

    print(f'Instance initial solution: {instance_name}', file=f)
    output, routes_list = instance.get_output(f)
    print(output, file=f)

    for vehicle in routes_list:
        name = os.path.splitext(instance_name)[0]
        depot_plot_dir = os.path.join(cwd, "route", name) 
        if not os.path.exists(depot_plot_dir): os.mkdir(depot_plot_dir)
        solution_plot_dir = os.path.join(cwd, "route", name, "initial solution") 
        if not os.path.exists(solution_plot_dir): os.mkdir(solution_plot_dir)
        path = os.path.join(solution_plot_dir, f"Vehicle {vehicle.id}")
        draw(routes_list[vehicle], True, path)
    
    
    start_time = time.time()
    results, count, temp_set, dist_set = sa_algorithm(instance)
    print("SA done for", instance_name, "run time:",
          time.time()-start_time, "loop times:", count)
    print("\n----------------------------------", file=f)
    print(f'Instance {instance_name} after 1 min', file=f)
    
    output, _ = results[0][0].get_output(f)
    print(output, file=f)
    print("Objective function count: ", results[0][1], file=f)
    print("\n----------------------------------", file=f)
    
    print(f'Instance {instance_name} after 5 min', file=f)
    output, _ = results[1][0].get_output(f)
    print(output, file=f)
    print("Objective function count: ", results[1][1], file=f)
    print("\n----------------------------------", file=f)
    print(f'Instance {instance_name} in the end')
    output, routes_list =  results[2][0].get_output(f)
    print(output, file=f)
    print("Objective function count: ", results[2][1], file=f)

    f.close()
    
    for vehicle in routes_list:
        name = os.path.splitext(instance_name)[0]
        depot_plot_dir = os.path.join(cwd, "route", name) 
        if not os.path.exists(depot_plot_dir): os.mkdir(depot_plot_dir)
        solution_plot_dir = os.path.join(cwd, "route", name, "final solution") 
        if not os.path.exists(solution_plot_dir): os.mkdir(solution_plot_dir)
        path = os.path.join(solution_plot_dir, f"Vehicle {vehicle.id}")
        draw(routes_list[vehicle], True, path)

    xpoints = temp_set
    ypoints = dist_set
    plt.plot(xpoints, ypoints)
    plt.xlim(max(xpoints), min(xpoints))
    plt.title("Biểu đồ thể hiện tốc độ cải thiện hàm mục tiêu " + instance_name)
    plt.xlabel("Nhiệt độ")
    plt.ylabel("Giá trị hàm mục tiêu")
    plt.show()
