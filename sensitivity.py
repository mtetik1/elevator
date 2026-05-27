import numpy as np
import matplotlib.pyplot as plt

import elevator_sim_zones as sim


def run_scenario(
    num_elevators: int,
    n_runs: int = 20,
    demand_factor: float = 1.0,
    speed_factor: float = 1.0,
    zone_probs_override: list[float] | None = None,
):

    orig_arrival_rate = sim.arrival_rate
    orig_speed = sim.ELEVATOR_SPEED
    orig_zone_probs = sim.zone_probs.copy()

    #scale lambda
    def scaled_arrival_rate(t):
        lam, direction = orig_arrival_rate(t)
        return lam * demand_factor, direction

    sim.arrival_rate = scaled_arrival_rate
    sim.ELEVATOR_SPEED = orig_speed * speed_factor


    if zone_probs_override is not None:
        # make sure they sum to 1
        total = sum(zone_probs_override)
        sim.zone_probs = [p / total for p in zone_probs_override]

    avg_waits = []
    max_waits = []
    avg_rides = []
    trips = []

    for seed in range(n_runs):
        avg_w, max_w, avg_r, n_trips = sim.run_simulation(
            seed=seed,
            num_elevators=num_elevators,
            verbose=False,
        )
        avg_waits.append(avg_w)
        max_waits.append(max_w)
        avg_rides.append(avg_r)
        trips.append(n_trips)

    # ---- restore originals ----
    sim.arrival_rate = orig_arrival_rate
    sim.ELEVATOR_SPEED = orig_speed
    sim.zone_probs = orig_zone_probs

    mean_avg_w = float(np.mean(avg_waits))
    mean_max_w = float(np.mean(max_waits))
    mean_avg_r = float(np.mean(avg_rides))
    mean_trips = float(np.mean(trips))

    return mean_avg_w, mean_max_w, mean_avg_r, mean_trips


if __name__ == "__main__":
    BASE_ELEVATORS = 2 
    RUNS = 20

    #demand
    demand_factors = [0.8, 1.0, 1.2]
    demand_results = []

    print("=== demand sensitivity ===")
    for f in demand_factors:
        res = run_scenario(
            num_elevators=BASE_ELEVATORS,
            n_runs=RUNS,
            demand_factor=f,
        )
        demand_results.append(res)
        print(
            f"  factor={f:.1f} → "
            f"mean_avg_wait={res[0]:.2f} min, "
            f"mean_max_wait={res[1]:.2f} min, "
            f"mean_ride={res[2]:.2f} min, "
            f"mean_trips={res[3]:.1f}"
        )

    #speed
    speed_factors = [0.8, 1.0, 1.2]
    speed_results = []

    print("\n==speed sensitivity ===")
    for f in speed_factors:
        res = run_scenario(
            num_elevators=BASE_ELEVATORS,
            n_runs=RUNS,
            speed_factor=f,
        )
        speed_results.append(res)
        print(
            f"  speed_factor={f:.1f} → "
            f"mean_avg_wait={res[0]:.2f} min, "
            f"mean_max_wait={res[1]:.2f} min, "
            f"mean_ride={res[2]:.2f} min, "
            f"mean_trips={res[3]:.1f}"
        )

    #xone tenant mix
    zone_scenarios = {
        "baseline": None,
        "upper_heavy": [0.2, 0.2, 0.3, 0.3],
        "even": [0.25, 0.25, 0.25, 0.25],
    }

    zone_labels = list(zone_scenarios.keys())
    zone_results = []

    print("\n=== Zone mix sensitivity ===")
    for label in zone_labels:
        override = zone_scenarios[label]
        res = run_scenario(
            num_elevators=BASE_ELEVATORS,
            n_runs=RUNS,
            zone_probs_override=override,
        )
        zone_results.append(res)
        print(
            f"  zone_mix={label} → "
            f"mean_avg_wait={res[0]:.2f} min, "
            f"mean_max_wait={res[1]:.2f} min, "
            f"mean_ride={res[2]:.2f} min, "
            f"mean_trips={res[3]:.1f}"
        )

    import matplotlib.pyplot as plt
    import numpy as np

    # Demand
    plt.figure()
    plt.plot(demand_factors,
             [r[0] for r in demand_results],
             marker="o")
    plt.xlabel("Demand factor")
    plt.ylabel("Mean average wait (min)")
    plt.title(f"Sensitivity to demand level (elevators = {BASE_ELEVATORS})")
    plt.grid(True)

    #Speed
    plt.figure()
    plt.plot(speed_factors,
             [r[0] for r in speed_results],
             marker="o")
    plt.xlabel("Speed factor")
    plt.ylabel("Mean average wait (min)")
    plt.title(f"Sensitivity to elevator speed (elevators = {BASE_ELEVATORS})")
    plt.grid(True)


    #zone mix
    plt.figure()
    x = np.arange(len(zone_labels))
    plt.bar(x, [r[0] for r in zone_results])
    plt.xticks(x, zone_labels)
    plt.ylabel("Mean average wait (min)")
    plt.title(f"Sensitivity to tenant mix (elevators = {BASE_ELEVATORS})")

    plt.tight_layout()
    plt.show()
