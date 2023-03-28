import matplotlib.pyplot as plt
from numpy import exp, loadtxt, pi, sqrt
import numpy as np
from lmfit import Model


def gaussian(x, amp, cen, wid):
    """1-d gaussian: gaussian(x, amp, cen, wid)"""
    return (amp / (sqrt(2*pi) * wid)) * exp(-(x-cen)**2 / (2*wid**2))

x = np.linspace(-1,1,500)
vol = np.linspace(1,2,500)
y = gaussian(x,2,0,vol)
print(y,x)

gmodel = Model(gaussian,independent_vars=['x','wid'])
result = gmodel.fit(y, x=x, wid=vol, amp=5, cen=5)

print(result.fit_report())

plt.plot(x, y, 'o')
plt.plot(x, result.init_fit, '--', label='initial fit')
plt.plot(x, result.best_fit, '-', label='best fit')
plt.legend()
plt.show()