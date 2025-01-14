import numpy as np
from typing import List, Optional, Union
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import shapiro


# Tukey's method
def tukeys_method(arr: np.ndarray, k: float):
    # Takes two parameters: dataframe & variable of interest as string
    q1 = np.quantile(arr, 0.25)
    q3 = np.quantile(arr, 0.75)
    iqr = q3 - q1
    le = q1 - k * iqr
    ue = q3 + k * iqr
    filtered_arr = arr[(arr >= le) & (arr <= ue)]
    return filtered_arr


def make_qqplot(y_tilde, k=1.5, MAKEPLOT=True):
    if k is not None:
        y_tilde = tukeys_method(y_tilde, k)

    # Fit a line to the QQ plot data
    osm, osr = (
        sm.ProbPlot(y_tilde).sample_quantiles,
        sm.ProbPlot(y_tilde).theoretical_quantiles,
    )

    # Perform linear regression on the QQ plot data
    slope, intercept, r_value, _, _ = stats.linregress(osr, osm)

    if MAKEPLOT:
        # Generate the QQ plot data
        sm.qqplot(y_tilde)

        # Plot the fitted line
        plt.plot(
            osr,
            intercept + slope * osr,
            "r",
            label=f"Fitted line: \ny={intercept:.2f}\nm={slope:.2f}\nR²={r_value**2:.2f}",
        )
        plt.legend()
    return slope, intercept, r_value


def test_normality(y_tilde: np.ndarray, k: Optional[float] = None):

    if k is not None:
        y_tilde = tukeys_method(y_tilde, k)

    stat, pval = shapiro(y_tilde)
    if pval < 0.05:
        print("The data is NOT normally distributed. p-value:", pval)
    else:
        print("The data IS normally distributed. p-value:", pval)

    return pval
