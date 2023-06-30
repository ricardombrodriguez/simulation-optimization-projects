import random
import numpy
from math import ceil

# Simulation constants
NUM_TYPE_A_SERVERS = 2
NUM_TYPE_B_SERVERS = 2
INTERARRIVAL_MEAN = 1  
TYPE_1_PROB = 0.8
TYPE_1_SERVICE_MEAN = 0.8  
TYPE_2_SERVICE_MEAN = (0.5, 0.7) 
MAX_SIMULATION_TIME = 1000
TIME_TICK_STEP = 10     # 10 ticks per second

# Performance tracking variables
type1_queue_delay = 0.0                 # Sum of the total delay of customers in type 1 queue
type1_queue_total_num_customers = 0     # Sum of the total number of customers that  passed in type 1 queue
type1_queue_avg_customers = 0           # Sum of the number of customers in type 1 queue throughout all ticks (10 times per unit)
type1_queue = []                        # Keep track of customers in queue and arrival time for type 1 queue
type2_queue_delay = 0.0                 # Sum of the total delay of customers in type 2 queue
type2_queue_total_num_customers = 0     # Sum of the total number of customers that  passed in type 2 queue
type2_queue_avg_customers = 0           # Sum of the number of customers in type 2 queue throughout all ticks (10 times per unit)
type2_queue = []                        # Keep track of customers in queue and arrival time for type 2 queue
server_utilization = { 
                        'A' : { index : 0.0 for index in range(1, NUM_TYPE_A_SERVERS+1) }, 
                        'B' : { index : 0.0 for index in range(1, NUM_TYPE_B_SERVERS+1) } 
                     }

# Event list (starts waiting for arrivals)
event_list = [ {'type': 'arrival', 'time': 0.0} ]

# Server status
server_status = { 
                  'A' : { index : False for index in range(1, NUM_TYPE_A_SERVERS+1) }, 
                  'B' : { index : False for index in range(1, NUM_TYPE_B_SERVERS+1) } 
                }

last_event_time = 0.0

# Simulation loop
while last_event_time <= MAX_SIMULATION_TIME:

    # Get next event (smallest time)
    event_index = None
    event_smallest_time = 1e9
    for index, event in enumerate(event_list):
        if event['time'] < event_smallest_time:
            event_index = index
            event_smallest_time = event['time']
    current_event = event_list.pop(event_index)

    # Check if there should be a tick to update the number of customers in each queue
    if ceil(last_event_time * TIME_TICK_STEP) != ceil(event_smallest_time * TIME_TICK_STEP):
        num_ticks = ceil(event_smallest_time * TIME_TICK_STEP) - ceil(last_event_time * TIME_TICK_STEP)  # number of time steps
        type1_queue_avg_customers += len(type1_queue) * num_ticks
        type2_queue_avg_customers += len(type2_queue) * num_ticks

    # Process arrival event
    if current_event['type'] == 'arrival':

        # Generate interrarival time for the next 'arrival event' (IID exponential random with a mean of 1 minute)
        interarrival_time = numpy.random.exponential(scale=INTERARRIVAL_MEAN)

        # Schedule next arrival event
        event_list.append({'type': 'arrival', 'time': current_event['time'] + interarrival_time})

        # Calculate customer type (TYPE 1 = 80% & TYPE 2 = 20%)
        if random.random() < TYPE_1_PROB:  # Type 1

            # Generate service time for the current event (IID exponential random with a mean of 0.8 minutes)
            service_time = numpy.random.exponential(scale=TYPE_1_SERVICE_MEAN)

            # Find type A server index (if one is available)
            typeA_server_index = None
            for index, status in server_status['A'].items():
                if not status:
                    typeA_server_index = index
                    break

            if typeA_server_index:  # Serve type 1 customer with a Type A available server

                # Schedule next departure event
                event_list.append({'type': 'departure', 'time': current_event['time'] + service_time, 'server': f'A{typeA_server_index}', 'customer_type': 1})

                # Type A server is now busy
                server_status['A'][typeA_server_index] = True

                # Update the correct type A server utilization time 
                server_utilization['A'][typeA_server_index] += service_time

            else:  # All type A servers are busy, check if there are type B servers available

                # Find type B server index (if one is available)
                typeB_server_index = None
                for index, status in server_status['B'].items():
                    if not status:
                        typeB_server_index = index
                        break

                if typeB_server_index: # Serve type 1 customer with a Type B available server

                    # Schedule next departure event
                    event_list.append({'type': 'departure', 'time': current_event['time'] + service_time, 'server': f'B{typeB_server_index}', 'customer_type': 1})

                    # Type B server is now busy
                    server_status['B'][typeB_server_index] = True

                    # Update the correct type B server utilization time 
                    server_utilization['B'][typeB_server_index] += service_time

                else:   # No servers available, customer joins type 1 FIFO queue

                    type1_queue.append(current_event)
                    type1_queue_total_num_customers += 1

        else:  # Type 2

            # Generate service time for the current event (uniform distribution between 0.5 and 0.7 minutes)
            service_time = random.uniform(TYPE_2_SERVICE_MEAN[0], TYPE_2_SERVICE_MEAN[1])

            # Find an available type A server
            typeA_server_index = None
            for index, status in server_status['A'].items():
                if not status:
                    typeA_server_index = index
                    break

            # Find an available type B server
            typeB_server_index = None
            for index, status in server_status['B'].items():
                if not status:
                    typeB_server_index = index
                    break

            if typeA_server_index and typeB_server_index:  # Serve type 2 customer with one type A and one type B server 

                # Schedule next departure event
                event_list.append({'type': 'departure', 'time': current_event['time'] + service_time, 'server': f'A{typeA_server_index} | B{typeB_server_index}', 'customer_type': 2})

                # Update the correct type A and type B servers to a busy status (true)
                server_status['A'][typeA_server_index] = True
                server_status['B'][typeB_server_index] = True

                # Update the correct type A and type B servers' utilization time 
                server_utilization['A'][typeA_server_index] += service_time
                server_utilization['B'][typeB_server_index] += service_time

            else:   # No servers available, customer joins type 2 FIFO queue

                type2_queue.append(current_event)
                type2_queue_total_num_customers += 1

    elif current_event['type'] == 'departure':

        if current_event['customer_type'] == 1:  # Type 1 customer

            if current_event['server'][0] == 'A':   # Customer in a type A server

                # Update type A server to available status
                typeA_server_idx = int(current_event['server'][1:])
                server_status['A'][typeA_server_idx] = False
            
            else:   # Customer in a type B server
                
                # Update type B server to available status
                typeB_server_index = int(current_event['server'][1:])
                server_status['B'][typeB_server_index] = False


        else:   # Type 2 customer

            # Update type A and type B servers to available status
            servers = current_event['server'].split(" | ")      # Example: splits "A1 | B1" into ["A1","B1"]
            typeA_server_idx = int(servers[0][1])               # Gets the server id/index of the type A server
            server_status['A'][typeA_server_idx] = False
            typeB_server_index = int(servers[1][1])             # Gets the server id/index of the type B server
            server_status['B'][typeB_server_index] = False

        # Type 2 queue customers take priority if both a type A and type B servers are available
        if ( (len(type2_queue) > 0) and (not all(status == True for status in server_status['A'].values())) and (not all(status == True for status in server_status['B'].values()))):

            # Remove first type 2 customer from FIFO queue
            queue_event = type2_queue.pop(0)
            
            # Generate service time for the current event (uniform distribution between 0.5 and 0.7 minutes)
            service_time = random.uniform(TYPE_2_SERVICE_MEAN[0], TYPE_2_SERVICE_MEAN[1])

            # Find an available type A server
            typeA_server_index = None
            for index, status in server_status['A'].items():
                if not status:
                    typeA_server_index = index
                    break

            # Find an available type B server
            typeB_server_index = None
            for index, status in server_status['B'].items():
                if not status:
                    typeB_server_index = index
                    break

            # Serve type 2 customer with one type A and one type B server (both values will be different than None)

            # Schedule next departure event
            event_list.append({'type': 'departure', 'time': current_event['time'] + service_time, 'server': f'A{typeA_server_index} | B{typeB_server_index}', 'customer_type': 2})

            type2_queue_delay += current_event['time'] - queue_event['time']    # Time waiting in queue

            # Update the correct type A and type B servers' utilization time 
            server_utilization['A'][typeA_server_index] += service_time
            server_utilization['B'][typeB_server_index] += service_time
        
            # Update the correct type A and type B servers to a busy status (false)
            server_status['A'][typeA_server_index] = False
            server_status['B'][typeB_server_index] = False

        elif len(type1_queue) > 0 and ( any(not status for status in server_status['A'].values() or any(not status for status in server_status['B'].values())) ):  # Serve type 1 customer

            # Remove first type 1 customer from FIFO queue
            queue_event = type1_queue.pop(0)
            
            # Generate service time for the current event (IID exponential random with a mean of 0.8 minutes)
            service_time = numpy.random.exponential(scale=TYPE_1_SERVICE_MEAN)

            # Find an available type A server
            typeA_server_index = None
            for index, status in server_status['A'].items():
                if not status:
                    typeA_server_index = index
                    break

            # Find an available type B server
            typeB_server_index = None
            for index, status in server_status['B'].items():
                if not status:
                    typeB_server_index = index
                    break

            if typeA_server_idx:    # Type A server available for type 1 customer

                event_list.append({'type': 'departure', 'time': current_event['time'] + service_time, 'server': f'A{typeA_server_index}', 'customer_type': 1})
                server_utilization['A'][typeA_server_index] += service_time


            else:   # Type B server available for type 1 customer

                event_list.append({'type': 'departure', 'time': current_event['time'] + service_time, 'server': f'B{typeB_server_index}', 'customer_type': 1})
                server_utilization['B'][typeB_server_index] += service_time
                server_status['B'][typeB_server_index] = False

            type1_queue_delay += current_event['time'] - queue_event['time']    # Time waiting in queue

    last_event_time = current_event['time']

# Calculate performance measures
print("======= expected average delay in queue ======= ")
print(f"[TYPE 1] {type1_queue_delay / type1_queue_total_num_customers} seconds")
print(f"[TYPE 2] {type2_queue_delay / type2_queue_total_num_customers} seconds")

print("======= expected time average number in queue for each type of customer ======= ")
print(f"[TYPE 1] {type1_queue_avg_customers / (MAX_SIMULATION_TIME * TIME_TICK_STEP)} ")
print(f"[TYPE 2] {type2_queue_avg_customers / (MAX_SIMULATION_TIME* TIME_TICK_STEP)} ")

print("======= expected proportion of time that each server spends on each type of customer ======= ")
for server_type, data in server_utilization.items():
    for server_id, time in data.items():
        print(f"[SERVER {server_type}{server_id} & TYPE 1] {time / MAX_SIMULATION_TIME}")
        print(f"[SERVER {server_type}{server_id} & TYPE 2] {1 - (time / MAX_SIMULATION_TIME)}")

