import os

import matplotlib.pyplot as plt
import numpy as np
from Dicom_RT_and_Images_to_Mask.src.DicomRTTool.ReaderWriter import DicomReaderWriter
from PlotScrollNumpyArrays.Plot_Scroll_Images import plot_scroll_Image
import SimpleITK as sitk
from NiftiResampler.ResampleTools import ImageResampler

path = r'K:\DosePlane'
cross_plane_field_size = 200  # in mm
physical_start = cross_plane_field_size//2*.9 - 5
if not os.path.exists("DosePlane_15X.nii.gz") or True:
    Dicom_reader = DicomReaderWriter(description='Examples', verbose=False, get_dose_output=True, Contour_Names=["Body"])
    Dicom_reader.set_contour_names_and_associations(contour_names=["Body"])
    Dicom_reader.walk_through_folders(path)
    Dicom_reader.get_images()
    Dicom_reader.get_dose()
    dose_plane = Dicom_reader.dose_handle[:, :, 0]
    sitk.WriteImage(dose_plane, "DosePlane_15X.nii.gz")
    """
    Bear in mind that virtual phantoms do not write out where the water is...The body contour keeps it though
    """
    # Resampler = ImageResampler()
    # dose_handle = Resampler.resample_image(input_image_handle=dose_handle,
    #                                        ref_resampling_handle=Dicom_reader.dicom_handle)
    """
    Iso center is still in the center (21x21x6), not the user origin. The phantom is 42x42x12cm
    Want point to be 9.9cm deep, so 3.3cm deeper
    """
    # desired_plane = dose_handle.TransformPhysicalPointToIndex((0, 33, 0))
    # dose_plane = dose_handle[:, desired_plane[1], :]
    # sitk.WriteImage(dose_plane, "DosePlane_15X.nii.gz")
else:
    dose_plane = sitk.ReadImage("DosePlane_15X.nii.gz")

plane_size = dose_plane.GetSize()
dose_plane_array = sitk.GetArrayFromImage(dose_plane)
spacing = dose_plane.GetSpacing()[1]
physical_center = dose_plane.TransformContinuousIndexToPhysicalPoint((plane_size[0]//2, plane_size[1]//2))
wanted_start = dose_plane.TransformPhysicalPointToIndex((physical_center[0], physical_center[1] - physical_start))
wanted_stop = dose_plane.TransformPhysicalPointToIndex((physical_center[0], physical_center[1] + physical_start))
dose_line = dose_plane_array[wanted_start[1]:wanted_stop[1], wanted_start[0]]
