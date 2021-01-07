import math
import enum
import random
import datetime
import logging
import names
import time
import threading
import os
from collections import OrderedDict

logging.basicConfig(filename='log.log', level=logging.DEBUG)

orders = []
global restaurants

average_speed = 1.5  # m/s
average_buffer_time = 30  # seconds
check_order_thresold = 3600  # 1hour
all_threads = []
driver_ping_display = 5
manage_order_time = 5
driver_reach_early_time =60
number_of_driver=4
number_of_restaurant=5
driver_buffer_request_time=30
driver_rest_time=30
restaurant_service_delay_time=30
accept_request_probability=50
request_accept_time=(0,20)
food_prep_time=(100,250)
number_of_food_items_per_restaurant=(5,8)
driver_location=(0,100)
restaurant_location=(0,100)

def get_request_accept_time():
    return random.randint(request_accept_time[0],request_accept_time[1])

def get_food_prep_time():
    return random.randint(food_prep_time[0],food_prep_time[1])

def get_food_items():
    return random.randint(number_of_food_items_per_restaurant[0],number_of_food_items_per_restaurant[1])

def get_driver_location():
    return (random.randint(driver_location[0],driver_location[1]),random.randint(driver_location[0],driver_location[1]))

def get_restaurant_location():
    return (random.randint(restaurant_location[0],restaurant_location[1]),random.randint(restaurant_location[0],restaurant_location[1]))

def get_first_driver_free_time(restaurant_index,target_location):
    drivers_of_restaurant = restaurants[restaurant_index].give_all_drivers_sorted()
    if len(drivers_of_restaurant) > 0:
        driver_first = restaurants[restaurant_index].list_of_drivers[drivers_of_restaurant[0]]
        return driver_first.get_driver_access_time(target_location) -datetime_to_seconds(datetime.datetime.now())
    else:
        drivers_of_restaurant = restaurants[restaurant_index].give_all_drivers_sorted(all_driver=True)
        driver_first = restaurants[restaurant_index].list_of_drivers[drivers_of_restaurant[0]]
        return driver_first.get_driver_access_time(target_location)-datetime_to_seconds(datetime.datetime.now())

def Add_order(order):
    global orders
    # orders.ap
    print("SDfsdf")
    if len(orders) <= 0:
        orders.append(order)
    else:
        is_inserted = False
        for i in range(len(orders)):
            print("Sdf", orders[i].pickup_time >= order.pickup_time, orders[i].pickup_time, order.pickup_time)
            if orders[i].pickup_time >= order.pickup_time:
                print("In", i)
                orders.insert(i, order)
                is_inserted = True
                break
        if not is_inserted:
            orders.append(order)
    print(orders)


def datetime_from_timestamp(timestamp_obj):
    return datetime.datetime.fromtimestamp(timestamp_obj)


def datetime_to_seconds(datetime_obj):
    return datetime.datetime.timestamp(datetime_obj)


def time_in_minutes(hours):
    fraction, whole = math.modf(hours / 60)
    return whole * 60 + fraction * 60


def minutes_to_hours(minutes):
    return minutes / 60


def distance_in_meters(location1, location2):
    return math.sqrt((location2[0] - location1[0]) ** 2 + (location2[1] - location1[1]) ** 2)


class Food:
    def __init__(self, prep_time):
        self.id = names.get_last_name()
        self.prep_time = prep_time

    def get_time(self):
        return self.prep_time


class DriverStatus(enum.Enum):
    Idel = 1
    Got_Request = 2
    Going_for_pickup = 3
    Waiting_for_Food_prep = 4
    Picked_up_order = 5
    Delivered = 6

class Driver:
    def __init__(self, location=(0, 0), driver_speed=1):
        self.id = names.get_full_name()
        self.location = location
        self.target_location = None
        self.status = DriverStatus.Idel
        self.driver_speed = average_speed # in meter per seconds
        self.buffer_request_time = driver_buffer_request_time  # in Seconds
        self.driver_free_time = datetime_to_seconds(datetime.datetime.now())
        self.driver_rest_time =driver_rest_time
        # self.got_request=False
        self.order = None

    # def driver_location_update(self):


    def request_for_food_delivery(self, order):
        if self.status==DriverStatus.Idel:
            self.status = DriverStatus.Got_Request
        logging.info(str(self.id) + " " + " got request of order " + str(order.id))
        is_accepted = False
        # while (r_time > 0):
        wait_time = get_request_accept_time()
        # logging.info("wait time for Driver "+)
        time.sleep(wait_time)
        numberList = ["a", "d"]
        driver_key = random.choices(numberList, weights=(accept_request_probability,100-accept_request_probability), k=1)
        logging.info(driver_key)
        if "a" in driver_key:
            logging.info(str(self.id) + " Driver accepted Order" + str(order.id))
            is_accepted = True
            self.target_location = order.restaurant_location
            self.status = DriverStatus.Going_for_pickup
            # self.next_ping_time=get_driver_access_time(self.target_location)
            self.driver_free_time = self.get_driver_access_time(self.target_location) + order.time_r2d
            self.order = order
            # break
        else:
            logging.info(str(self.id) + " Driver declined Order" + str(order.id))
            if self.status == DriverStatus.Got_Request:
                self.status = DriverStatus.Idel
            # break
            # time.sleep(driver_ping_display)
        return is_accepted

    def order_pickup(self):
        self.location=self.order.delivery_location
        self.target_location = self.order.delivery_location
        self.status = DriverStatus.Picked_up_order
        self.driver_free_time = datetime_to_seconds(datetime.datetime.now()) + self.order.time_r2d
        logging.info("Driver " + str(self.id) + " Picked up Order " + str(self.order.id) + " at " + str(
            datetime.datetime.now()) + " expected Delivery at " + str(datetime_from_timestamp(self.driver_free_time)))

    def order_delivered(self):
        self.location = self.order.delivery_location
        self.target_location = None
        self.status = DriverStatus.Delivered
        self.status = DriverStatus.Idel
        self.driver_free_time = datetime_to_seconds(datetime.datetime.now())
        logging.info(
            "Driver " + str(self.id) + " Delivered Order " + str(self.order.id) + " at " + str(datetime.datetime.now()))

    def get_driver_access_time(self, target_location):
        if self.status == DriverStatus.Idel:
            self.driver_free_time = datetime_to_seconds(datetime.datetime.now())
        return self.driver_free_time + self.buffer_request_time + distance_in_meters(self.location,
                                                                                     target_location) / self.driver_speed

class Restaurant:
    def __init__(self, list_of_foods, list_of_drivers, location):
        self.id = names.get_first_name()
        write_in_food(20 * "==" + "\n")
        write_in_food("Restaurant:" + str(self.id) + "\n")
        self.list_of_foods = list_of_foods
        for food in self.list_of_foods:
            write_in_food("Food:" + str(food.id) + "\n")
            write_in_food("Prep time:" + str(food.prep_time) + "\n")
        self.list_of_drivers = list_of_drivers
        self.location = location
        write_in_food("Location" + str(self.location) + "\n")
        write_in_food(20 * "==" + "\n")
        self.service_delay = restaurant_service_delay_time  # service delay in seconds

    def give_all_drivers_sorted(self,all_driver=False):
        drivers_dict = dict()
        for i, driver in enumerate(self.list_of_drivers):
            # print(driver.status)
            # if driver.status == DriverStatus.Idel or driver.status == DriverStatus.Picked_up_order or all_driver:
             if driver.status != DriverStatus.Got_Request:
                drivers_dict[i] = driver.get_driver_access_time(self.location) + self.service_delay
        list_of_indexed_driver_sorted = [i[0] for i in sorted(drivers_dict.items(), key=lambda x: x[1])]
        return [i for i in list_of_indexed_driver_sorted]


class Orders:
    def __init__(self, restaurant_index, food_index):
        self.id = random.randint(0, 1000000)
        is_correct_date = False
        self.driver = None
        is_correct_location = False
        order_log = "Id "+str(self.id)+"\n"
        while not is_correct_location:
            try:
                lat = input("Input Latitude between 0 to n where n is in meters : ")
                long = input("Input Longitude between 0 to n where n is in meters : ")
                self.delivery_location = (int(lat), int(long))
                is_correct_location = True
            except:
                print("Enter Correct lat long")
        self.restaurant_location = restaurants[restaurant_index].location
        self.distance_r2d = math.sqrt((self.restaurant_location[0] - self.delivery_location[0]) ** 2 + (
                    self.restaurant_location[1] - self.delivery_location[1]) ** 2)
        self.time_r2d = ((self.distance_r2d / average_speed) + restaurants[
            restaurant_index].service_delay + average_buffer_time)
        self.restaurant_index = restaurant_index
        self.food_index = food_index
        order_log += "Restaurant_Location " + str(self.restaurant_location) + "\n"
        order_log += "Restaurant to Home Distance " + str(self.distance_r2d) + "\n"
        order_log += "Restaurant to Home Time in seconds " + str(self.time_r2d) + " TravelTime " + str(
            self.distance_r2d / average_speed) + " Service Delay " + str(
            restaurants[restaurant_index].service_delay) + " Buffer Time " + str(average_buffer_time) + "\n"

        while not is_correct_date:
            try:
                date_and_time = input(
                    "Input Expected Delivery Date time in format of YYYY-MM-DD-HH-MM  enter 'i' for immediate delivery\n Example=> 2021-01-06-23-59 \n")
                # date_and_time="2021-1-5-19-40"
                if date_and_time == "i":
                    print("Delivery Date Immediate")
                    current_time = datetime_to_seconds(datetime.datetime.now())
                    service_delay = restaurants[restaurant_index].service_delay
                    prep_time = restaurants[restaurant_index].list_of_foods[food_index].prep_time
                    avg_buffer_time = average_buffer_time
                    r2dtime = self.time_r2d
                    drive2rtime=get_first_driver_free_time(self.restaurant_index,target_location=restaurants[self.restaurant_index].location)
                    new_delivery_time = current_time + service_delay + prep_time + avg_buffer_time + r2dtime + drive2rtime
                    self.expected_delivery_time = new_delivery_time
                    order_log += "Delivery time Expected " + str(datetime_from_timestamp(new_delivery_time)) + " Service Delay " + str(
                        service_delay) + " Prep Time " + str(prep_time) + " Buffer time " + str(
                        avg_buffer_time) + " Restaurant to Door " + str(r2dtime) + " Driver to Restaurant "+str(drive2rtime)+"\n"
                    # self.expected_delivery_time= )+restaurants[restaurant_index].service_delay+restaurants[restaurant_index].list_of_foods[food_index].prep_time+average_buffer_time+self.time_r2d
                else:
                    list_split = date_and_time.split("-")
                    self.expected_delivery_time = datetime_to_seconds(
                        datetime.datetime(int(list_split[0]), int(list_split[1]), int(list_split[2]),
                                          int(list_split[3]), int(list_split[4])))
                    # print("TIming",str(datetime.datetime.now()), datetime_from_timestamp(self.expected_delivery_time )
                    if (self.expected_delivery_time - datetime_to_seconds(
                            datetime.datetime.now()) < check_order_thresold):
                        current_time = datetime_to_seconds(datetime.datetime.now())
                        service_delay = restaurants[restaurant_index].service_delay
                        prep_time = restaurants[restaurant_index].list_of_foods[food_index].prep_time
                        avg_buffer_time = average_buffer_time
                        r2dtime = self.time_r2d
                        drive2rtime = get_first_driver_free_time(self.restaurant_index,target_location=restaurants[self.restaurant_index].location)
                        new_delivery_time = current_time + service_delay + prep_time + avg_buffer_time + r2dtime
                        order_log += "Delivery time Expected  " + str(datetime_from_timestamp(new_delivery_time)) + " Service Delay " + str(
                            service_delay) + " Prep Time " + str(prep_time) + " Buffer time " + str(
                            avg_buffer_time) + " Restaurant to Door" + str(r2dtime) +" Driver to Restaurant "+str(drive2rtime) +"\n"

                        self.expected_delivery_time = new_delivery_time
                        print("Your Order cannot be delivered at " + str(datetime_from_timestamp(
                            self.expected_delivery_time)) + " and it is Converted to Immediate order")
                    else:
                        print("Delivery Date", self.expected_delivery_time)
                        order_log += "Delivery Date Pre Order " + str(
                            datetime_from_timestamp(self.expected_delivery_time)) + "\n"

                is_correct_date = True
            except Exception as e:
                print(e)
        self.order_time = datetime.datetime.now()

        print("DSfsd")
        self.pickup_time = self.expected_delivery_time - self.time_r2d - driver_reach_early_time
        # if self.pickup_time
        order_log += "Pickup time " + str(datetime_from_timestamp(self.pickup_time)) + "\n"
        print("adf")
        # self.pickup_time=
        # self.predicted_delivery_time=
        print("pickup time", self.pickup_time, datetime_from_timestamp(self.pickup_time))
        print("Your Food " + str(
            restaurants[restaurant_index].list_of_foods[food_index].id) + " From Restaurant " + str(
            restaurants[restaurant_index].id) + " is Ordered at  " + str(self.order_time))
        write_in_order(order_log)


def create_foods(number_of_foods):
    return [Food(get_food_prep_time()) for i in range(number_of_foods)]


def create_drivers(number_of_drivers):
    return [Driver(location=get_driver_location()) for i in range(number_of_drivers)]


def create_Restaurants(number_of_restaurants, list_of_drivers):
    return [Restaurant(list_of_drivers=list_of_drivers, list_of_foods=create_foods(get_food_items()),
                       location=get_restaurant_location())for i in range(number_of_restaurants)]


def manage_order(order):
    # print()
    is_accepted = False
    driver_index = None
    drivers_index = restaurants[order.restaurant_index].give_all_drivers_sorted()

    while not is_accepted:
        drivers_index = restaurants[order.restaurant_index].give_all_drivers_sorted()
        for t_driver in drivers_index:
            # print(restaurants[order.restaurant_index].list_of_drivers[t_driver].status)
            # while restaurants[order.restaurant_index].list_of_drivers[t_driver].status!=DriverStatus.Idel:
            #     time.sleep(5)
            is_accepted = restaurants[order.restaurant_index].list_of_drivers[t_driver].request_for_food_delivery(order)
            # logging.info()
            if is_accepted:
                driver_index = t_driver
                break
        if driver_index == None:
            print("No Driver Accepted order of :" + str(order.id))
        else:
            while (restaurants[order.restaurant_index].list_of_drivers[driver_index].status != DriverStatus.Idel):
                if restaurants[order.restaurant_index].list_of_drivers[
                    driver_index].status == DriverStatus.Going_for_pickup:
                    logging.info(
                        "Pickup Time " + str(datetime_from_timestamp(order.pickup_time)) + str(datetime.datetime.now()))
                    while (order.pickup_time >= datetime_to_seconds(datetime.datetime.now())):

                        time.sleep(driver_ping_display)
                    restaurants[order.restaurant_index].list_of_drivers[driver_index].order_pickup()
                    logging.info("Delivery Time " + str(restaurants[order.restaurant_index].list_of_drivers[
                                                            driver_index].driver_free_time >= datetime_to_seconds(
                        datetime.datetime.now())) + str(datetime_from_timestamp(
                        restaurants[order.restaurant_index].list_of_drivers[driver_index].driver_free_time)) + str(
                        datetime.datetime.now()))
                    while (restaurants[order.restaurant_index].list_of_drivers[
                               driver_index].driver_free_time >= datetime_to_seconds(datetime.datetime.now())):
                        time.sleep(driver_ping_display)
                        # logging.info("Driver "+str(restaurants[order.restaurant_index].list_of_drivers[driver_index].id)+" Order "+str(order.id)+" Status "+str(restaurants[order.restaurant_index].list_of_drivers[driver_index].status)+" Estimated Delivery Time "+str(datetime_from_timestamp(restaurants[order.restaurant_index].list_of_drivers[driver_index].driver_free_time)))
                    restaurants[order.restaurant_index].list_of_drivers[driver_index].order_delivered()
                    break
                time.sleep(driver_ping_display)


def manage_order_driver():
    global orders
    while True:
        # logging.info([datetime_from_timestamp(i.expected_delivery_time) for i in orders])
        for order in orders:
            if order.pickup_time - datetime_to_seconds(datetime.datetime.now()) > check_order_thresold:
                break
            else:
                drivers_of_restaurant=restaurants[order.restaurant_index].give_all_drivers_sorted()
                if len(drivers_of_restaurant)>0:
                    driver_first = restaurants[order.restaurant_index].list_of_drivers[drivers_of_restaurant[0]]
                    print(driver_first)
                    print("First Driver Free time ", str(datetime_from_timestamp(
                        driver_first.get_driver_access_time(restaurants[order.restaurant_index].location))),
                          " Pickup Time " + str(
                              datetime_from_timestamp(order.pickup_time )))
                    if driver_first.get_driver_access_time(restaurants[
                                                               order.restaurant_index].location) < order.pickup_time :
                        th = threading.Thread(target=manage_order, args=(order,))
                        orders.remove(order)
                        th.start()
                        all_threads.append(th)
                else:
                    write_in_order("Finding Driver for your Order "+str(order.id))
            time.sleep(1)
        time.sleep(manage_order_time)


def write_in_order(text):
    f = open("order.log", "a")
    f.write(20 * "==" + "\n")
    f.write(text + "\n")
    f.write(20 * "==" + "\n")
    f.close()


def write_in_driver(text):
    f = open("driver.log", "a")
    f.write(20 * "==" + "\n")
    f.write(text + "\n")
    f.write(20 * "==" + "\n")
    f.close()


def write_in_food(text):
    f = open("restaurant.log", "a")
    # f.write(20 * "==" + "\n")
    f.write(text)
    # f.write(20 * "==" + "\n")
    f.close()

def view_driver():
    global restaurants
    while (True):
        for restaurant in restaurants:
            for driver in restaurant.list_of_drivers:
                # text=""
                text = str(driver.id) + "\n"
                text += str(driver.location) + "\n"
                text += str(driver.target_location) + "\n"
                text += str(driver.status) + "\n"
                text += str(driver.driver_free_time) + "\n"
                text += str(driver.order) + "\n"
                write_in_driver(text)
                time.sleep(1)


def view_order():
    order_status = False
    global restaurants

    while not order_status:
        # print()

        for i, restaurant in enumerate(restaurants):
            print("Press " + str(i) + "  for " + str(restaurant.id) + " Restaurant")
        print("Press e to Exit")
        input_key = input()
        if input_key in [str(i) for i in range(len(restaurants))]:
            # print(restaurants[int(input_key)1].list_of_foods)
            for i, food in enumerate(restaurants[int(input_key)].list_of_foods):
                print("Press " + str(i) + " for " + str(food.id) + " Food")
            print("Press e to Exit")
            input_key_food = input()
            if input_key_food in [str(i) for i in range(len(restaurants[int(input_key)].list_of_foods))]:
                order_object = Orders(int(input_key), int(input_key_food))
                global orders
                Add_order(order_object)
                order_status = True
                break
            elif input_key_food == "e":
                exit()
            else:
                print("Incorrect Food")
        elif input_key == "e":
            break;
        else:
            print("Incorrect Retaurant")


if __name__ == '__main__':
    open("driver.log", "w+")
    open("restaurant.log", "w+")
    open("order.log", "w+")
    # print(create_foods(5)[0].prep_time)
    drivers = create_drivers(number_of_driver)
    restaurants = create_Restaurants(number_of_restaurant, drivers)
    th_manage_driver = threading.Thread(target=manage_order_driver)
    th_view_driver = threading.Thread(target=view_driver)
    th_manage_driver.start()
    th_view_driver.start()
    all_threads.append(th_manage_driver)
    all_threads.append(th_view_driver)
    try:
        while True:
            print("Press 1 for new Order")
            input_key = input()
            if input_key == "1":
                view_order()
    except KeyboardInterrupt:
        pass
    finally:
        os.remove("log.log")
        os.remove("driver.log")
        os.remove("order.log")
        os.remove("restaurant.log")
        # print("Joined")
        for thr in all_threads:
            if thr.is_alive():
                thr.join()