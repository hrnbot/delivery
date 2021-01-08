import math
location=(3,4)
target_location=(0,0)
import time
def distance_in_meters(location1, location2):
    return math.sqrt((location2[0] - location1[0]) ** 2 + (location2[1] - location1[1]) ** 2)

print("Distance ",distance_in_meters(location, target_location) )

index=0
while distance_in_meters(location, target_location) >= 1:
    # if distance_in_meters(location, target_location) <= 1:
    #     temp_location = target_location
    # else:
    print(str(index),"Distance ", distance_in_meters(location, target_location))
    index+=1
    theta = math.atan2(target_location[0] - location[0], target_location[1] - location[1])
    # theta *= (180 / 3.14)

    temp_location = (location[0] + math.sin(theta), location[1] + math.cos(theta))
    location = temp_location
    print(temp_location, target_location, location)
    time.sleep(0.5)

print("Distance ", distance_in_meters(location, target_location))
