# DES using numpy for elevator capacity scenarios in high rise construction projects
A simple discrete-event simulation model for exploring elevator capacity scenarios in high rise construction projects.
The model simulates worker movements between the ground floor and different floor zones during a construction workday. It includes time-dependent arrival patterns, elevator travel time, boarding and unloading time, and stochastic variation between simulation runs.

The purpose of the model is to support early stage comparison of elevator capacity alternatives, such as using one, two, or three elevators, and to estimate their effects on worker waiting time, ride time, and completed trips.

## Files
- `elevator_sim_zones.py`  
  Main simulation model, including floor zones, worker arrivals, elevator movement, and performance metrics.

- `run_replications.py`  
  Runs multiple replications for different elevator scenarios and plots summary results.

## Requirements

```bash
pip install simpy numpy matplotlib
