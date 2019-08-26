from .core.log import with_log
from .core.constants import PLOT_PATH

from .plot.histogram import plot_histogram
from .plot.gaussian import plot_gaussian
from .plot.fmri import plot_fmri
from .plot.scatter import plot_scatter
from .plot.smooth import plot_smooth


@with_log
def Plot_Results(lg):

    for i in PLOT_PATH.glob('*'):
        i.unlink()

    plot_fmri(PLOT_PATH)

    plot_gaussian(PLOT_PATH)
    plot_histogram(PLOT_PATH)
    plot_scatter(PLOT_PATH)
    plot_smooth(PLOT_PATH)
