import numpy as np
import matplotlib.pyplot as plt

import elevator_sim_zones as sim  # this is your main sim file


def run_many(num_elevators: int, n_runs: int = 20):
    avg_waits = []
    max_waits = []
    avg_rides = []
    trips = []

    print(f"===running scenario with {num_elevators} elevators===")

    for seed in range(n_runs):
        print(f"running seed {seed}, elevators = {num_elevators}")
        avg_w, max_w, avg_r, n_trips = sim.run_simulation(
            seed=seed,
            num_elevators=num_elevators,
            verbose=False,                 )
        avg_waits.append(avg_w)
        max_waits.append(max_w)
        avg_rides.append(avg_r)
        trips.append(n_trips)

    mean_avg_w = float(np.mean(avg_waits))
    mean_max_w = float(np.mean(max_waits))
    mean_avg_r = float(np.mean(avg_rides))
    mean_trips = float(np.mean(trips))

    print("===summary ===")
    print(f"runs: {n_runs}")
    print(f"elevators: {num_elevators}")
    print(f"mean avg wait (min): {mean_avg_w:.2f}")
    print(f"mean max wait (min): {mean_max_w:.2f}")
    print(f"mean avg ride (min): {mean_avg_r:.2f}")
    print(f"mean trips: {mean_trips:.1f}")
    print()

    return mean_avg_w, mean_max_w, mean_avg_r, mean_trips


if __name__ == "__main__":
    elevator_options = [1, 2, 3]

    mean_avg_waits = []
    mean_max_waits = []
    mean_avg_rides = []
    mean_trips = []

    for k in elevator_options:
        m_avg, m_max, m_ride, m_tr = run_many(k, n_runs=20)
        mean_avg_waits.append(m_avg)
        mean_max_waits.append(m_max)
        mean_avg_rides.append(m_ride)
        mean_trips.append(m_tr)

    #plot
    x = elevator_options

    fig, axes = plt.subplots(2, 2, figsize=(9, 7))

    #mean avg wait
    axes[0, 0].bar(x, mean_avg_waits)
    axes[0, 0].set_title("Mean worker waiting time")
    axes[0, 0].set_xlabel("number of elevators")
    axes[0, 0].set_ylabel("min")

    #mean max wait
    axes[0, 1].bar(x, mean_max_waits)
    axes[0, 1].set_title("Mean of max waits")
    axes[0, 1].set_xlabel("number of elevators")
    axes[0, 1].set_ylabel("min")

    #mean avg ride time
    axes[1, 0].bar(x, mean_avg_rides)
    axes[1, 0].set_title("Mean ride time")
    axes[1, 0].set_xlabel("number of elevators")
    axes[1, 0].set_ylabel("min")

    #mean trips per day
    axes[1, 1].bar(x, mean_trips)
    axes[1, 1].set_title("Mean number of trips")
    axes[1, 1].set_xlabel("number of elevators")
    axes[1, 1].set_ylabel("trips")

    fig.suptitle("Elevator performance vs number of elevators", y=1.02)
    fig.tight_layout()
    plt.show()
