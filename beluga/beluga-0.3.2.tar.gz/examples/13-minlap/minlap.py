"""Brachistochrone example."""
import beluga
import logging
from math import pi

import matplotlib.pyplot as plt

ocp = beluga.OCP('minlap')

# Define independent variables
ocp.independent('t', '1')

# Define equations of motion
ocp.state('n', '(sin(xi)*u + cos(xi)*u)/s_dot', '1')
ocp.state('xi', '(Omega - C/(1-C*n)*(cos(xi)*u - sin(xi)*v))/s_dot', '1')
ocp.state('m*u', '(2*(cdel*Fxf - sdel*Fyf + Fxr) + m*Omega*v - kv*u**2)/s_dot', '1')
ocp.state('m*v', '(2*(sdel*Fxf + cdel*Fyf + Fyr) - m*Omega*u)/s_dot', '1')
ocp.state('Omega', '(2*(Lf*(sdel*Fxf + cdel*Fyf) - Lr*Fyr))/(s_dot*Izz)', '1')
ocp.state('alpha_r', '(u*arctan((v-Omega*Lr)/u) - u*alpha_r)/(sigyr*s_dot)', '1')
ocp.state('alpha_f', '(u*arctan((Lf*Omega*cdel - sdel*u + cdel*v)/(Lf*Omega*sdel + cdel*u + sdel*v)) - u*alpha_f)/(sigyf*s_dot)', '1')
ocp.state('kap_r', '(u*(kap_ro - kap_r))/(sigxr*s_dot)', '1')
ocp.state('kap_f', '(u*(kap_fo - kap_f))/(sigxf*s_dot)', '1')
ocp.state('delta', '(vdel)/s_dot', '1')
ocp.state('s', 's_dot', '1')

ocp.quantity('cdel', 'cos(delta)')
ocp.quantity('sdel', 'sin(delta)')
ocp.quantity('s_dot', '(cos(xi)*u - sin(xi)*v)/(1 - C*n)')

# Define controls
ocp.control('vdel', '1')
ocp.control('kap_ro', '1')
ocp.control('kap_fo', '1')

# Define constants

ocp.constant('m', 2100, '1')
ocp.constant('g', 9.82, '1')
ocp.constant('Izz', 3900, '1')
ocp.constant('kv', 0, '1')
ocp.constant('Lf', 1.3, '1')
ocp.constant('Lr', 1.5, '1')
ocp.constant('sigxf', 0.5, '1')
ocp.constant('sigxr', 0.5, '1')
ocp.constant('sigyf', 0.3, '1')
ocp.constant('sigyr', 0.3, '1')
ocp.constant('kap_ro_max', 0.2, '1')
ocp.constant('kap_fo_max', 0.2, '1')
ocp.constant('delta_max', 75*pi/180, '1')
ocp.constant('v_delta_max', 60*pi/180, '1')
ocp.constant('n_max', 2.5, '1')
ocp.constant('mu_xf', 1.2, '1')
ocp.constant('Cxf', 1.69, '1')
ocp.constant('Cxaf', 1.09, '1')
ocp.constant('Bxf', 11.7, '1')
ocp.constant('Bx1f', 12.4, '1')
ocp.constant('Bx2f', -10.8, '1')
ocp.constant('mu_xr', 1.2, '1')
ocp.constant('Cxr', 1.69, '1')
ocp.constant('Cxar', 1.09, '1')
ocp.constant('Bxr', 11.1, '1')
ocp.constant('Bx1r', 12.4, '1')
ocp.constant('Bx2r', -10.8, '1')
ocp.constant('mu_yf', 0.935, '1')
ocp.constant('Cyf', 1.7, '1')
ocp.constant('Cykf', 1.08, '1')
ocp.constant('Byf', 8.86, '1')
ocp.constant('By1f', 6.46, '1')
ocp.constant('By2f', 4.20, '1')
ocp.constant('mu_yr', 0.961, '1')
ocp.constant('Cyr', 1.7, '1')
ocp.constant('Cykr', 1.08, '1')
ocp.constant('Byr', 7.0, '1')
ocp.constant('By1r', 6.46, '1')
ocp.constant('By2r', 4.20, '1')
ocp.constant('S', 357.08, '1')

ocp.constant('U0', 50/3.6, '1')
# ocp.constant('x_f', 0, 'm')
# ocp.constant('y_f', 0, 'm')

# Define costs
ocp.path_cost('1', '1')

# Define constraints
ocp.constraints() \
    .initial('n', '1') \
    .initial('xi', '1') \
    .initial('v', '1') \
    .initial('u - U0', '1') \
    .initial('Omega', '1') \
    .initial('delta', '1') \
    .initial('alpha_r', '1') \
    .initial('alpha_f', '1') \
    .initial('u', '1') \
    .terminal('n', '1') \
    .terminal('xi', '1')

ocp.scale(m='y', s='y/v', kg=1, rad=1, nd=1)

bvp_solver = beluga.bvp_algorithm('Shooting', algorithm='SLSQP')

guess_maker = beluga.guess_generator(
    'auto',
    start=[0, 0, 0],          # Starting values for states in order
    costate_guess=-0.1,
    control_guess=[-pi/2],
    use_control_guess=True
)

continuation_steps = beluga.init_continuation()

continuation_steps.add_step('bisection') \
                .num_cases(21) \
                .const('x_f', 1) \
                .const('y_f', -1)

beluga.add_logger(logging_level=logging.DEBUG, display_level=logging.DEBUG)

sol_set = beluga.solve(
    ocp=ocp,
    method='indirect',
    bvp_algorithm=bvp_solver,
    steps=continuation_steps,
    guess_generator=guess_maker,
    autoscale=True
)

sol = sol_set[-1][-1]

plt.plot(sol.y[:, 0], sol.y[:, 1])
plt.show()

print(sol.y[0])
print(sol.dual[0])
