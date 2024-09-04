# src/data_processing/data_processor.py

import numpy as np


def normalize_spectrum(spectral_data: np.ndarray) -> np.ndarray:
    """
    Normalize a spectral map. Works with both 1D and 2D arrays.

    Args:
        spectral_data (np.ndarray): Input spectral array to be normalized.

    Returns:
        np.ndarray: Normalized spectral array.
    """
    print(f"Input spectral data shape: {spectral_data.shape}")

    if spectral_data.ndim == 1:
        # For 1D data, normalize by the median of the entire array
        median_spectrum = np.nanmedian(spectral_data)
        normalized_spectrum = spectral_data / median_spectrum
    elif spectral_data.ndim == 2:
        # For 2D data, normalize each wavelength by its median across time
        median_spectrum = np.nanmedian(spectral_data, axis=1, keepdims=True)
        normalized_spectrum = spectral_data / median_spectrum
    else:
        raise ValueError(f"Unexpected number of dimensions: {spectral_data.ndim}")

    print(f"Output normalized spectrum shape: {normalized_spectrum.shape}")
    return normalized_spectrum
