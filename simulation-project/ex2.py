import numpy as np
import matplotlib.pyplot as plt
import argparse

# Exercise 2.1 -  trace the evolution of x(t), and y(t), using the Forward Euler method given the method input arguments
def lotka_volterra_forward_euler(x0, y0, alpha, beta, delta, gamma, time_step, max_time):
    times = np.arange(0, max_time + time_step, time_step)   # Fills up a zero-valued array from [0, max_time[ in *time_step* (delta_t) steps
    n = len(times)                                          
    x = np.zeros(n)     # Number of preys
    y = np.zeros(n)     # Number of predators                
    x[0] = float(x0)           # Initial number of preys
    y[0] = float(y0)           # Initial number of predators
    # Compute the predator-prey population evolution over n iterations
    for i in range(1, n):
        x[i] = x[i-1] + (alpha * x[i-1] - beta * x[i-1] * y[i-1]) * time_step
        y[i] = y[i-1] + (- gamma * y[i-1] + delta * x[i-1] * y[i-1]) * time_step
    return times, x, y

def lotka_volterra_runge_kutta(x0, y0, alpha, beta, delta, gamma, time_step, max_time):
    times = np.arange(0, max_time + time_step, time_step)
    n = len(times)
    x = np.zeros(n)
    y = np.zeros(n)
    x[0] = x0
    y[0] = y0    
    # Compute the predator-prey population evolution over n iterations
    for i in range(1, n):
        k1x = alpha * x[i-1] - beta * x[i-1] * y[i-1]
        k1y = delta * x[i-1] * y[i-1] - gamma * y[i-1]
        k2x = alpha * (x[i-1] + k1x*time_step/2) - beta * (x[i-1] + k1x*time_step/2) * (y[i-1] + k1y*time_step/2)
        k2y = delta * (x[i-1] + k1x*time_step/2) * (y[i-1] + k1y*time_step/2) - gamma * (y[i-1] + k1y*time_step/2)
        k3x = alpha * (x[i-1] + k2x*time_step/2) - beta * (x[i-1] + k2x*time_step/2) * (y[i-1] + k2y*time_step/2)
        k3y = delta * (x[i-1] + k2x*time_step/2) * (y[i-1] + k2y*time_step/2) - gamma * (y[i-1] + k2y*time_step/2)
        k4x = alpha * (x[i-1] + k3x*time_step) - beta * (x[i-1] + k3x*time_step) * (y[i-1] + k3y*time_step)
        k4y = delta * (x[i-1] + k3x*time_step) * (y[i-1] + k3y*time_step) - gamma * (y[i-1] + k3y*time_step)
        x[i] = x[i-1] + time_step/6 * (k1x + 2*k2x + 2*k3x + k4x)
        y[i] = y[i-1] + time_step/6 * (k1y + 2*k2y + 2*k3y + k4y)
    return times, x, y

# Parse command line arguments in order to redirect ot the Forward Euler or the Runge Kutta method (Lotka Volterra variations)
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CLI Interface to the predator-prey populations simulation program using the Lotka-Volterra model')
    parser.add_argument('x0', type=float, help='Initial number of preys (population density)')
    parser.add_argument('y0', type=float, help='Initial number of predators (population density)')
    parser.add_argument('alpha', type=float, help='Maximum prey per capita growth rate')
    parser.add_argument('beta', type=float, help='Effect of the presence of predators on the prey growth rate')
    parser.add_argument('delta', type=float, help="Effect of the presence of prey on the predator's growth rate")
    parser.add_argument('gamma', type=float, help="Predator's per capita death rate")
    parser.add_argument('time_step', type=float, help='Time step interval')
    parser.add_argument('max_time', type=float, help='Time of the simulaiton')
    parser.add_argument('--method', type=str, default='euler', choices=['euler', 'runge_kutta'], help='Lotka Volterra variation method')
    args = parser.parse_args()

    # Redirection to the correct Lotka Volterra method 
    if args.method == 'euler':
        times, x, y = lotka_volterra_forward_euler(args.x0, args.y0, args.alpha, args.beta, args.delta, args.gamma, args.time_step, args.max_time)
    elif args.method == 'runge_kutta':
        times, x, y = lotka_volterra_runge_kutta(args.x0, args.y0, args.alpha, args.beta, args.delta, args.gamma, args.time_step, args.max_time)
    else:
        print("[ERROR] Invalid method.")
        exit(0)

    # Plot the graph after the simulation is done with the predator-prey populations evolution over time
    plt.plot(times, x, color="blue", label='Preys')
    plt.plot(times, y, color="red", label='Predators')
    plt.xlabel('Time - t')
    plt.ylabel('Population')
    plt.legend()
    plt.show()
