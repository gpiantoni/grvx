import plotly.graph_objs as go
from .paths import get_path
from bidso.utils import read_tsv


SHIFT = 'middle'  # middle / whole


def plot_histogram(parameters, frequency_band):

    summary_tsv = get_path(parameters, 'summary_tsv', frequency_band=frequency_band)
    if summary_tsv is None:
        return

    summary = read_tsv(summary_tsv)

    figs = []
    for value_type in ('r2_at_peak', 'size_at_peak', 'size_at_concave'):

        if value_type in ('size_at_peak', 'size_at_concave'):
            bin_size = 1
            dtick = 4
            max_val = parameters['fmri']['at_elec']['kernel_end']

        elif value_type == 'r2_at_peak':
            bin_size = .1
            dtick = 0.2
            max_val = 1

        if SHIFT == 'middle':
            xbins = dict(
                start=bin_size / -2,
                end=max_val + bin_size / 2,
                size=bin_size,
                )

        else:
            xbins = dict(
                start=0,
                end=max_val + bin_size,
                size=bin_size,
                )

        values = summary[value_type]
        traces = [
            go.Histogram(
                x=values,
                xbins=xbins,
                marker=dict(
                    color='black',
                    ),
                ),
            ]

        layout = go.Layout(
            barmode='stack',
            showlegend=False,
            xaxis=dict(
                range=(0, max_val + bin_size / 2),
                dtick=dtick,
                ),
            yaxis=dict(
                dtick=1,
                ),
            )

        fig = go.Figure(
            data=traces,
            layout=layout,
            )

        figs.append(fig)

    return figs
