from pickle import load
from shutil import rmtree
from numpy import arange, genfromtxt
from numpy import concatenate as concat
from numpy import argsort, array
import plotly.graph_objs as go
from wonambi.trans import montage, timefrequency
from wonambi.trans import concatenate, select, math
from bidso.utils import read_tsv

from nibabel import load as nload

from .paths import get_path


THRESH = 10
TR = 0.608


def revision(parameters):

    plot_dir = parameters['paths']['output'] / 'revision'
    try:
        rmtree(plot_dir)
    except OSError:
        pass
    plot_dir.mkdir(exist_ok=True, parents=True)

    fig = timeseries_fmri(parameters)
    fig.write_image(str(plot_dir / 'timeseries_fmri.svg'))

    fig = timeseries_ieeg(parameters)
    fig.write_image(str(plot_dir / 'timeseries_ieeg.svg'))

    figs = headmotions(parameters)
    for name, fig in figs.items():
        fig.write_image(str(plot_dir / f'{name}.svg'))


def timeseries_fmri(parameters):
    fmri_dir = parameters['paths']['output'] / 'workflow' / 'fmri'
    subject = parameters['plot']['subject']
    subject = 'delft'
    fmri_subj_dir = fmri_dir / f'_subject_{subject}'

    regressor_file = next(fmri_subj_dir.rglob('design.mat'))
    thresh_file = next(fmri_subj_dir.rglob('thresh_zstat1.nii.gz'))
    timeseries_file = next(fmri_subj_dir.rglob('filtered_func_data.nii.gz'))

    subj_dir = parameters['paths']['input'] / f'sub-{subject}'
    events_fmri_file = next(subj_dir.glob('ses-*/func/*_events.tsv'))

    thresh = nload(thresh_file).get_fdata()
    i_vox = thresh >= THRESH
    timeseries = nload(timeseries_file).get_fdata()
    fmri = timeseries[i_vox]
    t_fmri = arange(timeseries.shape[3]) * TR

    regressor = genfromtxt(regressor_file, skip_header=5)

    traces = [
        go.Scatter(
            x=t_fmri,
            y=fmri.mean(axis=0),
            line=dict(
                color='black',
                ),
        ),
        go.Scatter(
            x=t_fmri,
            y=regressor,
            yaxis='y2',
        ),
        ]
    fig = go.Figure(
        data=traces,
        layout=dict(
            yaxis2=dict(
                overlaying='y',
                side='right',
            ),
            shapes=event_shapes(events_fmri_file),
        )
        )

    return fig


def timeseries_ieeg(parameters):

    ieeg_dir = parameters['paths']['output'] / 'workflow' / 'ieeg'
    subject = parameters['plot']['subject']
    freq = parameters['ieeg']['ecog_compare']['frequency_bands'][-1]

    ieeg_subj_dir = ieeg_dir / f'_subject_{subject}'

    ieeg_compare_file = next(ieeg_subj_dir.glob(f'_frequency_{freq[0]}.{freq[1]}/ecog_compare/sub-*_compare.tsv'))
    ieeg0_file = next(ieeg_subj_dir.rglob('*_task-motoractive_*_ieeg.pkl'))
    ieeg1_file = next(ieeg_subj_dir.rglob('*_task-motorbaseline_*_ieeg.pkl'))

    subj_dir = parameters['paths']['input'] / f'sub-{subject}'
    events_ieeg_file = next(subj_dir.glob('ses-*/ieeg/*_events.tsv'))

    dat0 = compute_quick_spectrogram(ieeg0_file, freq)
    dat1 = compute_quick_spectrogram(ieeg1_file, freq)

    dat = dat0._copy()
    dat.data = concat([dat0.data, dat1.data])
    dat.axis['time'] = concat([dat0.time, dat1.time])
    dat.axis['chan'] = concat([dat0.chan, dat1.chan])

    dat = concatenate(dat, axis='time')

    ieeg_compare = read_tsv(ieeg_compare_file)

    chans = ieeg_compare['channel'][ieeg_compare['measure'] > 10]
    x0 = math(select(dat, chan=chans), operator_name='mean', axis='chan')

    t = dat.time[0]
    x = x0(trial=0)

    i_t = argsort(t)

    traces = [
        go.Scatter(
            x=t[i_t],
            y=x[i_t],
            line=dict(
                color='black',
            )
        ),

    ]
    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            yaxis=dict(
                rangemode='tozero',
                ),
            shapes=event_shapes(events_ieeg_file),
        ))

    return fig


def compute_quick_spectrogram(ieeg_file, freq):
    with ieeg_file.open('rb') as f:
        data = load(f)

    # TODO: from parameters
    reref = 'average'
    method = 'spectrogram'
    duration = 2
    data = montage(data, ref_to_avg=True, method=reref)
    tf = timefrequency(data, method=method, duration=duration)

    dat0 = math(select(tf, freq=freq), operator_name='mean', axis='freq')
    return dat0


def event_shapes(events_file):
    events = read_tsv(events_file)
    shapes = []

    for ev in events:
        if ev['trial_type'] == 'move':
            shapes.append(
                dict(
                    type='rect',
                    layer='below',
                    x0=ev['onset'],
                    x1=ev['onset'] + ev['duration'],
                    y0=0,
                    y1=1,
                    yref='paper',
                    fillcolor='gray',
                    line=dict(
                        width=0,
                    )
                )
                )
    return shapes


def headmotions(parameters):

    fmri_dir = parameters['paths']['output'] / 'workflow' / 'fmri'

    freq = parameters['ieeg']['ecog_compare']['frequency_bands'][-1]
    summary_tsv = get_path(parameters, 'summary_tsv', frequency_band=freq)
    summary = read_tsv(summary_tsv)

    figs = {}
    for mc_type in ('prefiltered_func_data_mcf_rel_mean.rms', 'prefiltered_func_data_mcf_abs_mean.rms'):
        mc = []
        for summ in summary:
            fmri_subj_dir = fmri_dir / f'_subject_{summ["subject"]}'
            mc_file = next(fmri_subj_dir.rglob(mc_type))
            mc.append(genfromtxt(mc_file))
        mc = array(mc)

        for value_type in ('r2_at_peak', 'size_at_peak'):
            fig = go.Figure(data=[
                go.Scatter(
                    x=mc,
                    y=summary[value_type],
                    text=summary["subject"],
                    mode='markers',
                )
                ], layout=go.Layout(
                    title=dict(
                        text=mc_type + ' ' + value_type,
                        ),
                    xaxis=dict(
                        rangemode='tozero',
                        ),
                    yaxis=dict(
                        rangemode='tozero',
                        ),
                    ))
            name = mc_type[:-4] + '_' + value_type
            figs[name] = fig

    return figs
