from pathlib import Path
from numpy import gradient
import plotly.graph_objs as go

from bidso.utils import read_tsv
from bidso import file_Core


def plot_smooth(PLOT_PATH):
    for one_tsv in Path('/Fridge/users/giovanni/projects/grvx/derivatives/nipype/grvx/corr_fmri_ecog_summary/output/rsquared').glob('*.tsv'):
        results = read_tsv(one_tsv)
        subject = file_Core(one_tsv).subject

        traces = [
            dict(
                x=results['Kernel'],
                y=results['Rsquared'],
                marker=dict(
                    color='black',
                    ),
                ),
            ]

        layout = go.Layout(
            xaxis=dict(
                dtick=4,
                range=(0, 20),
                tickfont=dict(
                    size=8,
                    ),
                ),
            yaxis=dict(
                dtick=0.1,
                rangemode='tozero',
                tickfont=dict(
                    size=8,
                    ),
                ),
            )

        fig = go.Figure(
            data=traces,
            layout=layout,
            )
        fig.write_image(str(PLOT_PATH / f'smooth_r2_{subject}.svg'))

        traces = [
            dict(
                x=results['Kernel'],
                y=gradient(gradient(results['Rsquared'])),
                marker=dict(
                    color='black',
                    ),
                ),
            ]

        layout.update(dict(
            yaxis=dict(
                dtick=0.002,
                range=(-0.005, 0.005),
                ),
            ))

        fig = go.Figure(
            data=traces,
            layout=layout,
            )
        fig.write_image(str(PLOT_PATH / f'smooth_deriv_{subject}.svg'))
