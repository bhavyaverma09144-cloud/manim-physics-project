import numpy as np
from scipy.integrate import solve_ivp

def double_pendulum_ode(t, y, L1, L2, m1, m2, g):
    theta1, omega1, theta2, omega2 = y
    delta = theta2 - theta1

    d1 = L1 * (2 * m1 + m2 - m2 * np.cos(2 * theta1 - 2 * theta2))
    d2 = L2 * (2 * m1 + m2 - m2 * np.cos(2 * theta1 - 2 * theta2))

    dtheta1 = omega1
    dtheta2 = omega2

    num1 = -g * (2 * m1 + m2) * np.sin(theta1) - m2 * g * np.sin(theta1 - 2 * theta2) - 2 * np.sin(delta) * m2 * (omega2**2 * L2 + omega1**2 * L1 * np.cos(delta))
    domega1 = num1 / d1

    num2 = 2 * np.sin(delta) * (omega1**2 * L1 * (m1 + m2) + g * (m1 + m2) * np.cos(theta1) + omega2**2 * L2 * m2 * np.cos(delta))
    domega2 = num2 / d2

    return [dtheta1, domega1, dtheta2, domega2]

def simulate_pendulum(t_max=10.0, fps=30):
    t_eval = np.linspace(0, t_max, int(t_max * fps))
    y0 = [np.pi / 2, 0.0, np.pi / 2, 0.0]
    params = (1.0, 1.0, 1.0, 1.0, 9.81) # L1, L2, m1, m2, g
    
    sol = solve_ivp(
        lambda t, y: double_pendulum_ode(t, y, *params),
        [0, t_max],
        y0,
        t_eval=t_eval,
        method='RK45',
        rtol=1e-6,
        atol=1e-8
    )
    return sol.t, sol.y
  
