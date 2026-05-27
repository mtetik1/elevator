import simpy
import random
import numpy as np

FLOORS = 40
FLOOR_HEIGHT = 3.2
ELEVATOR_SPEED = 45 / 60.0
CAPACITY = 12

SIM_TIME = 8 * 60 * 60 + 15

ZONES = {
    "zone1": {"floors": range(1, 11), "workers": 40},
    "zone2": {"floors": range(11, 21), "workers": 30},
    "zone3": {"floors": range(21, 31), "workers": 30},
    "zone4": {"floors": range(31, 41), "workers": 20},
}

total_workers = sum(z["workers"] for z in ZONES.values())
zone_names = list(ZONES.keys())
zone_probs = [ZONES[z]["workers"] / total_workers for z in zone_names]

wait_times = []
ride_times = []
trip_count = 0


def travel_time_sec(f_from, f_to):
    dist = abs(f_to - f_from) * FLOOR_HEIGHT
    return dist / ELEVATOR_SPEED


def arrival_rate(t):
        m = t / 60.0

    if 0 <= m < 30:          #07:00–07:30 morning up peak
        return 4.0, "up"
    elif 30 <= m < 210:      #07:30–10:30 steadyish
        return 1.0, "mixed"
    elif 210 <= m < 220:     # 10:30–10:40lunch down
        return 2.0, "down"
    elif 220 <= m < 250:     # 10:40–11:10 lunch break
        return 0.5, "mixed"
    elif 250 <= m < 265:     # 11:10–11:25 lunch up
        return 2.0, "up"
    elif 265 <= m < 465:     # 11:25–14:45 steady afternoon
        return 1.0, "mixed"
    elif 465 <= m < 495:     # 14:45–15:15 end day down peak
        return 3.0, "down"
    else:
        return 0.2, "mixed"


class Elevator:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.current_floor = 0
        self.res = simpy.Resource(env, capacity=1)

    def ride(self, origin, dest):
        #move to origin
        t1 = travel_time_sec(self.current_floor, origin)
        if t1 > 0:
            yield self.env.timeout(t1)
        self.current_floor = origin

        # boarding
        board = random.uniform(10.0, 20.0)
        yield self.env.timeout(board)

        # travel to dest
        t2 = travel_time_sec(origin, dest)
        if t2 > 0:
            yield self.env.timeout(t2)
        self.current_floor = dest

        # unboarding
        unload = random.uniform(5.0, 10.0)
        yield self.env.timeout(unload)


class ElevatorSystem:
    def __init__(self, env, num_elevators):
        self.env = env
        self.elevators = [Elevator(env, f"Elev_{i}") for i in range(num_elevators)]

    def pick_elevator(self):
        choices = []
        q_lengths = []
        for e in self.elevators:
            choices.append(e)
            q_lengths.append(len(e.res.queue))
        min_q = min(q_lengths)
        idxs = [i for i, q in enumerate(q_lengths) if q == min_q]
        return choices[random.choice(idxs)]


def worker_trip(env, name, system, origin, dest):
    global wait_times, ride_times, trip_count

    elev = system.pick_elevator()
    arrive = env.now
    with elev.res.request() as req:
        yield req
        wait = env.now - arrive
        wait_times.append(wait)

        start_ride = env.now
        yield env.process(elev.ride(origin, dest))
        end_ride = env.now

        ride = end_ride - start_ride
        ride_times.append(ride)
        trip_count += 1


def trip_generator(env, system):
    trip_id = 0
    while True:
        lam, direction = arrival_rate(env.now)

        inter = random.expovariate(lam / 60.0)
        yield env.timeout(inter)

        trip_id += 1

        zone_name = random.choices(zone_names, weights=zone_probs)[0]
        floors = list(ZONES[zone_name]["floors"])

        if direction == "up":
            origin = 0
            dest = random.choice(floors)
        elif direction == "down":
            origin = random.choice(floors)
            dest = 0
        else:  # mixed
            if random.random() < 0.5:
                origin, dest = 0, random.choice(floors)
            else:
                origin, dest = random.choice(floors), 0

        env.process(worker_trip(env, f"trip_{trip_id}", system, origin, dest))

def run_simulation(seed=42, num_elevators=1, verbose=True):
    global wait_times, ride_times, trip_count
    random.seed(seed)
    np.random.seed(seed)
    wait_times = []
    ride_times = []
    trip_count = 0

    env = simpy.Environment()
    system = ElevatorSystem(env, num_elevators)
    env.process(trip_generator(env, system))

    env.run(until=SIM_TIME)

    if len(wait_times) == 0:
        return 0.0, 0.0, 0.0, 0

    waits = np.array(wait_times) / 60.0  # to minutes
    rides = np.array(ride_times) / 60.0

    avg_wait = waits.mean()
    max_wait = waits.max()
    avg_ride = rides.mean()

    if verbose:
        print(f"sim done, seed = {seed}, elevators = {num_elevators}")
        print(f"trips: {trip_count}")
        print(f"avg wait (min): {avg_wait:.2f}")
        print(f"max wait (min): {max_wait:.2f}")
        print(f"avg ride (min): {avg_ride:.2f}")

    return avg_wait, max_wait, avg_ride, trip_count


if __name__ == "__main__":
    run_simulation(seed=42, num_elevators=1)
