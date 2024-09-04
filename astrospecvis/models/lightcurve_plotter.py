import os
import plotly.graph_objs as go
import numpy as np
from astrospecvis.utils.utils import bin_flux_array
import logging
import traceback

logger = logging.getLogger(__name__)


def ensure_output_directory(file_path):
    """Ensure the output directory exists."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created output directory: {directory}")


def plot_enhanced_lightcurve_map(flux_data: np.ndarray, wavelengths: np.ndarray, times: np.ndarray,
                                 title: str, bin_size: int = 25, output_file: str = 'enhanced_lightcurve_map.html',
                                 max_frames: int = 30, plot_type: str = 'variability'):
    """
    Create an enhanced interactive 3D surface plot of a lightcurve map.

    Args:
        flux_data (np.ndarray): 2D array of flux values.
        wavelengths (np.ndarray): 1D array of wavelength values.
        times (np.ndarray): 1D array of time values.
        title (str): Title of the plot.
        bin_size (int): Size of bins for flux array.
        output_file (str): Name of the output HTML file.
        max_frames (int): Maximum number of frames for animation.
        plot_type (str): Type of plot to create ('variability' or 'flux').
    """
    try:
        logger.info(f"Starting plot_enhanced_lightcurve_map for {title}")
        logger.info(f"Initial flux data shape: {flux_data.shape}")
        logger.info(f"Wavelengths shape: {wavelengths.shape}")
        logger.info(f"Times shape: {times.shape}")
        logger.info(f"Using bin_size: {bin_size}")
        logger.info(f"Using max_frames: {max_frames}")
        logger.info(f"Plot type: {plot_type}")

        # Convert bin_size to integer in case it is passed as a string
        bin_size = int(bin_size)

        # Bin the data
        flux_data = bin_flux_array(flux_data, bin_size)
        times = times[::bin_size]  # Adjust times array to match binned data
        logger.info(f"Flux data shape after binning: {flux_data.shape}")

        num_wavelengths, num_times = flux_data.shape
        logger.info(f"Number of wavelengths and time points: {num_wavelengths}, {num_times}")

        if num_times == 0:
            logger.error("No time points available after binning. Unable to create plot.")
            return

        # Create mesh grid for plotting
        time_hours = (times - times.min()) * 24  # Convert to hours
        time_grid, wavelength_grid = np.meshgrid(time_hours, wavelengths)

        # Ensure time_grid and wavelength_grid have the same shape as flux_data
        time_grid = time_grid[:, :num_times]
        wavelength_grid = wavelength_grid[:, :num_times]

        logger.info(f"Time grid shape: {time_grid.shape}")
        logger.info(f"Wavelength grid shape: {wavelength_grid.shape}")

        if plot_type == 'variability':
            # Calculate variability
            median_flux = np.nanmedian(flux_data, axis=1, keepdims=True)
            z_data = np.where(np.isfinite(flux_data), ((flux_data / median_flux) - 1) * 100, np.nan)
            colorbar_title = 'Variability %'
        elif plot_type == 'flux':
            z_data = flux_data
            colorbar_title = 'Flux (Jy)'
        else:
            raise ValueError(f"Invalid plot_type: {plot_type}")

        logger.info(f"Z data shape before slicing: {z_data.shape}")

        # Slice the data to remove the first 60 wavelength points
        wavelength_grid = wavelength_grid[60:, :]
        time_grid = time_grid[60:, :]
        z_data = z_data[60:, :]

        logger.info(f"Z data shape after slicing: {z_data.shape}")
        logger.info(f"Time grid shape after slicing: {time_grid.shape}")
        logger.info(f"Wavelength grid shape after slicing: {wavelength_grid.shape}")

        # Check for valid data after slicing
        if not np.any(np.isfinite(z_data)):
            logger.error("No finite values in z_data after slicing. Unable to create plot.")
            return

        # Define wavelength ranges for different compounds
        ch4_range = (2.14, 2.5)
        co_range = (4.5, 5.05)

        # Create masks for each compound
        ch4_mask = (wavelength_grid >= ch4_range[0]) & (wavelength_grid <= ch4_range[1])
        co_mask = (wavelength_grid >= co_range[0]) & (wavelength_grid <= co_range[1])

        logger.info(f"CH4 mask shape: {ch4_mask.shape}")
        logger.info(f"CO mask shape: {co_mask.shape}")

        custom_colorscale = [
            [0, 'rgb(0, 0, 100)'],  # Dark blue for low values
            [0.5, 'rgb(0, 255, 255)'],  # Cyan for middle values
            [1, 'rgb(255, 255, 0)']  # Yellow for high values
        ]

        # Create the surface plots
        surface_full = go.Surface(
            x=time_grid, y=wavelength_grid, z=z_data,
            surfacecolor=z_data, colorscale=custom_colorscale,
            colorbar=dict(title=colorbar_title, titleside='right', titlefont=dict(size=14),
                          tickfont=dict(size=12), len=0.75, thickness=15),
            opacity=1, name='Full Spectrum'
        )

        surface_ch4 = go.Surface(
            x=time_grid, y=wavelength_grid, z=np.where(ch4_mask, z_data, np.nan),
            surfacecolor=np.where(ch4_mask, z_data, np.nan), colorscale=custom_colorscale,
            opacity=1, showscale=False, name='CH4 Band'
        )

        surface_co = go.Surface(
            x=time_grid, y=wavelength_grid, z=np.where(co_mask, z_data, np.nan),
            surfacecolor=np.where(co_mask, z_data, np.nan), colorscale=custom_colorscale,
            opacity=1, showscale=False, name='CO Band'
        )

        # Create frames for animation
        frames = []
        frame_times = np.linspace(time_hours.min(), time_hours.max(), max_frames)
        for i, time_point in enumerate(frame_times):
            time_diff = np.abs(time_grid - time_point)
            opacity = np.exp(-time_diff ** 2 / (2 * 5 ** 2))  # Gaussian window

            frame = go.Frame(
                data=[go.Surface(
                    x=time_grid, y=wavelength_grid, z=z_data,
                    surfacecolor=z_data * opacity, colorscale=custom_colorscale, opacity=1
                )],
                name=f'frame_{i}'
            )
            frames.append(frame)

        # Set up the layout
        layout = go.Layout(
            title=title,
            scene=dict(
                xaxis=dict(title='Time (hours)'),
                yaxis=dict(title='Wavelength (µm)'),
                zaxis=dict(title=colorbar_title),
                aspectmode='manual',
                aspectratio=dict(x=1.3, y=1, z=1)
            ),
            updatemenus=[
                dict(type="buttons", showactive=False, buttons=[
                    dict(label="Play", method="animate",
                         args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}]),
                    dict(label="Pause", method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}])
                ], x=0.1, y=0, xanchor="right", yanchor="top"),
                dict(buttons=[
                    dict(label="Full Spectrum", method="update", args=[{"visible": [True, False, False]}]),
                    dict(label="CH4 Band", method="update", args=[{"visible": [False, True, False]}]),
                    dict(label="CO Band", method="update", args=[{"visible": [False, False, True]}])
                ], direction="down", pad={"r": 10, "t": 10}, showactive=True, x=0.9, y=1.1, xanchor="right",
                    yanchor="top")
            ],
            sliders=[dict(
                active=0,
                currentvalue={"prefix": "Time: ", "suffix": " hours"},
                pad={"t": 50},
                steps=[dict(
                    method='animate',
                    args=[[f'frame_{i}'], {'frame': {'duration': 100, 'redraw': True}, 'mode': 'immediate'}],
                    label=f'{time_point:.1f}'
                ) for i, time_point in enumerate(frame_times)]
            )],
            template='plotly_dark',
            margin=dict(l=0, r=0, b=0, t=30),
            width=1000,
            height=800
        )

        # Create the figure and add the surface plots
        fig = go.Figure(data=[surface_full, surface_ch4, surface_co], layout=layout, frames=frames)

        # Ensure the output directory exists
        ensure_output_directory(output_file)

        # Save the plot as an HTML file
        logger.info(f"Saving plot as HTML file: {output_file}")
        fig.write_html(output_file)

        logger.info(f"Enhanced plot creation complete for {title}")
    except Exception as e:
        logger.error(f"An error occurred in plot_enhanced_lightcurve_map: {str(e)}")
        logger.error(traceback.format_exc())
        raise


def plot_specific_wavelength_lightcurves(flux_data: np.ndarray, wavelengths: np.ndarray, times: np.ndarray,
                                         title: str, output_file: str, bin_size: int = 25):
    """
    Extract and plot light curves for specific wavelengths of interest, particularly CH4 and CO bands.

    Args:
        flux_data (np.ndarray): 2D array of flux values.
        wavelengths (np.ndarray): 1D array of wavelength values.
        times (np.ndarray): 1D array of time values.
        title (str): Title of the plot.
        output_file (str): Name of the output HTML file.
        bin_size (int): Size of bins for flux array.
    """
    try:
        logger.info(f"Starting plot_specific_wavelength_lightcurves for {title}")

        # Bin the data
        bin_size = int(bin_size)  # Ensure bin_size is an integer
        flux_data = bin_flux_array(flux_data, bin_size)
        times = times[::bin_size]  # Adjust times array to match binned data

        # Convert times to hours
        time_hours = (times - times.min()) * 24

        # Define wavelength ranges for CH4 and CO
        ch4_range = (2.14, 2.5)
        co_range = (4.5, 5.05)

        # Find indices for CH4 and CO bands
        ch4_indices = np.where((wavelengths >= ch4_range[0]) & (wavelengths <= ch4_range[1]))[0]
        co_indices = np.where((wavelengths >= co_range[0]) & (wavelengths <= co_range[1]))[0]

        # Extract light curves
        ch4_lightcurve = np.mean(flux_data[ch4_indices, :], axis=0)
        co_lightcurve = np.mean(flux_data[co_indices, :], axis=0)

        # Normalize light curves
        ch4_lightcurve = ch4_lightcurve / np.median(ch4_lightcurve)
        co_lightcurve = co_lightcurve / np.median(co_lightcurve)

        # Create traces
        trace_ch4 = go.Scatter(x=time_hours, y=ch4_lightcurve, mode='lines', name='CH4 Band')
        trace_co = go.Scatter(x=time_hours, y=co_lightcurve, mode='lines', name='CO Band')

        # Create layout
        layout = go.Layout(
            title=title,
            xaxis=dict(title='Time (hours)'),
            yaxis=dict(title='Normalized Flux'),
            legend=dict(x=0, y=1, traceorder='normal'),
            template='plotly_dark'
        )

        # Create figure and add traces
        fig = go.Figure(data=[trace_ch4, trace_co], layout=layout)

        # Ensure the output directory exists
        ensure_output_directory(output_file)

        # Save the plot as an HTML file
        logger.info(f"Saving plot as HTML file: {output_file}")
        fig.write_html(output_file)

        logger.info(f"Specific wavelength light curves plot creation complete for {title}")
    except Exception as e:
        logger.error(f"An error occurred in plot_specific_wavelength_lightcurves: {str(e)}")
        logger.error(traceback.format_exc())
        raise
