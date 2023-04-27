from .util import *
from math import ceil
import random
from vincenty import vincenty as vct
import pandas as pd
import json


class Customer:
    def __init__(self, cust_no, name, address, x, y, demand, ready_time, due_date, service_time):
        self.cust_no = cust_no
        self.name = name
        self.address = address
        self.x = x
        self.y = y
        self.demand = demand
        self.ready_time = ready_time
        self.due_date = due_date
        self.service_time = service_time
        self.is_served = False
        self.vehicle_num = None

    def copy(self):
        return Customer(self.cust_no, self.x, self.y, self.demand, self.ready_time, self.due_date, self.service_time)

    def served(self, vehicle_num):
        self.is_served = True
        self.vehicle_num = vehicle_num

    def unserve(self):
        self.is_served = False
        self.vehicle_num = None

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)

    def __eq__(self, other):
        return self.cust_no == other.cust_no


class Vehicle:
    def __init__(self, id, depo, max_capacity, min_capacity=0):
        self.id = id
        self.x = depo.x
        self.y = depo.y
        self.max_capacity = max_capacity
        self.min_capacity = min_capacity
        self.capacity = max_capacity
        self.last_service_time = 0
        self.service_route = [(depo, 0)]
        self.total_distance = 0
        self.depo = depo
        self.speed = 5/6

    def serve_customer(self, customer):
        # ràng buộc thời gian serve khách và capacity
        # print("Vehicle", self.id, "try serve customer", customer.cust_no, "with result:", self.capacity, customer.demand, not (self.capacity <= customer.demand))
        if self.capacity <= customer.demand:
            return False
        # ràng buộc thời gian về kho
        # if self.depo.due_date < ceil(vincenty(customer, self)/self.speed) + self.last_service_time + customer.service_time + ceil(vincenty(customer, self.depo)/self.speed):
        #     return False
        dist = vincenty(customer, self)
        self.x = customer.x
        self.y = customer.y
        self.capacity -= customer.demand
        self.last_service_time += ceil(dist/self.speed)
        self.service_route += [(customer, self.last_service_time)]
        self.last_service_time += customer.service_time
        customer.served(self.id)
        self.total_distance += dist
        if self.capacity < self.min_capacity:
            self.return_home()
        return True

    def serve_customer_force(self, customer):
        # serve customer nếu ready_time của next_cust > thời gian di chuyển + last_service_time của cust cũ
        # last_service_time của cust cũ = ready_time của next_cust - thời gian di chuyển
        if customer.ready_time > ceil(vincenty(customer, self)/self.speed) + self.last_service_time:
            last_service_time = self.last_service_time
            self.last_service_time = customer.ready_time - \
                ceil(vincenty(customer, self)/self.speed)
            if self.serve_customer(customer):
                return True
            else:
                self.last_service_time = last_service_time
        return False
# Kết thúc tại kho

    def return_home(self):
        if self.x != self.depo.x or self.y != self.depo.y:
            # capacity 4.2.3
            self.capacity = self.max_capacity
            self.last_service_time += ceil(vincenty(self,
                                           self.depo)/self.speed)
            self.service_route += [(self.depo, self.last_service_time)]
            self.total_distance += vincenty(self, self.depo)
            self.x = self.depo.x
            self.y = self.depo.y

    # remove cust đã serve
    def remove_customer(self, customer):
        customer_idx = [route_node[0]
                        for route_node in self.service_route].index(customer)
        del self.service_route[customer_idx]
        self.capacity += customer.demand
        customer.unserve()
    # xe đi đến khách hàng nào thì phải rời khỏi khách hàng đó
        for i, (curr_customer, curr_time) in enumerate(self.service_route[customer_idx:]):
            prev_customer, prev_time = self.service_route[customer_idx + i - 1]
            new_time = prev_time + prev_customer.service_time + \
                ceil(vincenty(prev_customer, curr_customer)/self.speed)
            new_time = max(new_time, curr_customer.ready_time)
            self.service_route[customer_idx + i] = (curr_customer, new_time)

        next_customer = self.service_route[customer_idx][0]
        prev_customer = self.service_route[customer_idx - 1][0]
        self.total_distance -= (vincenty(customer, next_customer) +
                                vincenty(customer, prev_customer))
        self.total_distance += vincenty(prev_customer, next_customer)
        self.last_service_time = self.service_route[-1][1]

        self.reset_vehicle_used()

    def try_to_serve_customer(self, new_customer):
        # nếu route empty gán khách hàng có khung thời gian gần nhất với thời điểm hiện tại cho xe.
        if len(self.service_route) == 1:
            return self.serve_customer(new_customer) or self.serve_customer_force(new_customer)
        shuffled = list(range(1, len(self.service_route)))
        random.shuffle(shuffled)
        for i in shuffled:
            vehicle = Vehicle(self.id, self.depo,
                              self.max_capacity, self.min_capacity)
            vehicle.hard_reset_vehicle()
            index = i
            should_use_route = True
            new_customer.is_served = False
            for e, (customer, curr_time) in enumerate(self.service_route[1:]):
                if e + 1 == index:
                    if not vehicle.serve_customer(new_customer):
                        if not vehicle.serve_customer_force(new_customer):
                            should_use_route = False
                            break
                if not vehicle.serve_customer(customer):
                    if not vehicle.serve_customer_force(customer):
                        should_use_route = False
                        break
            if not should_use_route or not new_customer.is_served:
                new_customer.is_served = False
                continue
            self.service_route = vehicle.service_route[:]
            self.last_service_time = vehicle.last_service_time
            self.capacity = vehicle.capacity
            self.total_distance = vehicle.total_distance
            return True
        return False

    def hard_reset_vehicle(self):
        self.service_route = [(self.depo, 0)]
        self.last_service_time = 0
        self.capacity = self.max_capacity
        self.total_distance = 0

    def reset_vehicle_used(self):
        if self.service_route[0] == self.service_route[1]:
            self.hard_reset_vehicle()

    def __str__(self):
        return f'self.id = {self.id}; x={self.x}; y={self.y}; capacity={self.capacity}; last_service_time={self.last_service_time}; {self.service_route}'


def all_served(customers, b=False):
    result = True
    for c in customers:
        if not c.is_served:
            if b:
                print(c)
            result = False

    return result


class Instance:
    def __init__(self, num_vehicles, capacity, customer_list):
        assert (
            num_vehicles > 0 and capacity > 0
        ), f'Number of vehicles and their capacity must be positive! {num_vehicles}, {capacity}'
        self.num_vehicles = num_vehicles
        self.capacity = capacity

        # Bắt đầu tại kho
        depo = customer_list[0]
        self.vehicles = [Vehicle(i, depo, capacity)
                         for i in range(num_vehicles)]
        assert (
            customer_list[0].cust_no == 0 and customer_list[0].ready_time == 0 and customer_list[0].demand == 0
        ), f'Customer list must contain depot with customer number 0!'
        self.customer_list = [customer_list[0]] + \
            sorted(customer_list[1:], key=lambda c: c.ready_time)

    def __getitem__(self, key):
        return self.customer_list[key]

    def __str__(self):
        result = f'Vehicle Number: {self.num_vehicles}; Capacity: {self.capacity};'
        for customer in self.customer_list:
            result += f'\n{customer}'
        return result

    def sort_by_ready_time(self):
        self.customer_list.sort(key=lambda c: c.ready_time)

    def find_initial_solution(self):
        for i, v in enumerate(self.vehicles):
            # print("Vehicle:", i)
            while True:
                # self.customer_list.sort(key = lambda c: vincenty(c,v)/v.speed + c.ready_time)
                found = False
                for customer in self.customer_list:
                    if customer.is_served or customer.cust_no == 0:
                        continue

                    if v.serve_customer(customer):
                        # print("Vehicle:", v.id, "can serve", customer.cust_no)
                        found = True
                        break

                # if not found:
                #     print("not found")
                #     for customer in self.customer_list:
                #         if customer.is_served or customer.cust_no == 0:
                #             continue

                        # if v.serve_customer_force(customer):
                        #     found = True
                        #     break

                if not found:
                    break

            self.customer_list.sort(key=lambda c: c.cust_no)
            if all_served(self.customer_list[1:]):
                break
        self.customer_list.sort(key=lambda c: c.cust_no)

        for vehicle in self.vehicles:
            if vehicle.last_service_time == 0:
                continue
            vehicle.return_home()

        if not all_served(self.customer_list[1:], True):
            print("Not all vehicles has been served!\n")

    def generate_random_neighbour(self):
        # rand_cust = self.customer_list[random.randint(1, len(self.customer_list) - 1)]
        if len(self.customer_list) <= 1:
            return

        rand_cust = random.choices(self.customer_list[1:], [
                                   1./len(self.vehicles[c.vehicle_num].service_route) for c in self.customer_list[1:]], k=1)[0]
        current_serving_vehicle = self.vehicles[rand_cust.vehicle_num]
        current_serving_vehicle.remove_customer(rand_cust)
        v = None
        while not rand_cust.is_served:
            if self.get_neighbour(rand_cust):
                return
            self.get_neighbour(rand_cust, True)

    def get_neighbour(self, customer, force=False):
        shuffled = [i for i in range(0, len(self.vehicles) - 1)]
        random.shuffle(shuffled)
        for vehicle_num in shuffled:
            vehicle = self.vehicles[vehicle_num]
            if force or vehicle.last_service_time != 0:
                if vehicle.try_to_serve_customer(customer):
                    return True

    def get_output(self, f=None):
        dist = 0
        result = ""
        count = 1

        routes_list = {}
        for vehicle in self.vehicles:
            points = []
            if vehicle.last_service_time == 0:
                continue
            vehicle.return_home()
            dist += vehicle.total_distance
            result += f'Vehicle {vehicle.id}: '

            length = len(vehicle.service_route)

            route = ""
            customer_info = ""
            for i in range(0, length):
                node = vehicle.service_route[i]
                if node[0].cust_no == 0.0:
                    route += f'(Depot, service time {node[1]})'
                    customer_info += f'\t\tDepot: {node[0]}\n'
                else:
                    route += f'(Customer {node[0].cust_no}, service time {node[1]})'
                if i < length - 1:
                    route += ' -> '
                    customer_info += f'\t\tCustomer: {node[0]} \n'

                points.append((node[0].x, node[0].y, node[0].cust_no))

            result += route + '\n' + customer_info + '\n'
            count += 1
            routes_list[vehicle] = points
        print("Number vehicle:", count-1, file=f)
        print("Total distance:", dist, file=f)
        return f'{i-1}\n{result}{dist}', routes_list

    def get_total_distance_and_vehicles(self):
        dist = 0
        vehicles_used = 0
        for vehicle in self.vehicles:
            if vehicle.last_service_time == 0:
                continue
            vehicle.return_home()
            vehicles_used += 1
            dist += vehicle.total_distance
        return dist, vehicles_used

    def __str__(self):
        return self.get_output()


def load_from_file(filepath_txt, filepath_xlsx):
    i = 0
    num_vehicles = 0
    capacity = 0

    with open(filepath_txt, encoding="utf-8") as f:
        line = f.readline()
        while line:
            if not line.strip():  # skip empty lines
                line = f.readline()
                continue
            if i == 2:  # number of vehicles and capacity
                params = [int(p) for p in line.split()]
                num_vehicles = params[0]
                capacity = params[1]
                break
            # elif i >= 5: # customer info
            #     params = [p for p in line.split()]
            #     print(params)
            #     customer_list.append(Customer(*params))

            i += 1
            line = f.readline()
    df = pd.read_excel(filepath_xlsx)
    customer_list = []
    for i in df.index:
        customer_list.append(Customer(
            cust_no=int(i),
            name=str(df['NAME'][i]),
            address=str(df['ADDRESS'][i]),
            x=float(df['X'][i]),
            y=float(df['Y'][i]),
            demand=float(df['DEMAND'][i]),
            ready_time=float(df['START'][i]),
            due_date=float(df['END'][i]),
            service_time=float(df['SERVICE TIME'][i]),
        ))
    return Instance(num_vehicles, capacity, customer_list)


def vincenty(x: any, y: any):
    return vct([x.x, x.y], [y.x, y.y])
