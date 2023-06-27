import os

import matplotlib.pyplot as plt
import numpy as np
from DicomRTTool.ReaderWriter import DicomReaderWriter
from PlotScrollNumpyArrays.Plot_Scroll_Images import plot_scroll_Image
import SimpleITK as sitk
from NiftiResampler.ResampleTools import ImageResampler

path = r'K:\DosePlane'
if not os.path.exists("Dose_15X.nii.gz") or True:
    Dicom_reader = DicomReaderWriter(description='Examples', verbose=False, get_dose_output=True, Contour_Names=["Body"])
    Dicom_reader.set_contour_names_and_associations(contour_names=["Body"])
    Dicom_reader.walk_through_folders(path)
    Dicom_reader.get_images_and_mask()
    dose_handle = Dicom_reader.dose_handle
    sitk.WriteImage(dose_handle, "Dose_15X.nii.gz")
    """
    Bear in mind that virtual phantoms do not write out where the water is...The body contour keeps it though
    """
    Resampler = ImageResampler()
    dose_handle = Resampler.resample_image(input_image_handle=dose_handle,
                                           ref_resampling_handle=Dicom_reader.dicom_handle)
    dose_array = sitk.GetArrayFromImage(dose_handle)
    """
    Iso center is still in the center (21x21x6), not the user origin. The phantom is 42x42x12cm
    Want point to be 9.9cm deep, so 3.3cm deeper
    """
    desired_plane = dose_handle.TransformPhysicalPointToIndex((0, 33, 0))
    dose_plane = dose_handle[:, desired_plane[1], :]
    sitk.WriteImage(dose_plane, "DosePlane_15X.nii.gz")
else:
    dose_plane = sitk.ReadImage("DosePlane_15X.nii.gz")

dose_plane_array = sitk.GetArrayFromImage(dose_plane)
spacing = dose_plane.GetSpacing()[1]
start = dose_plane.TransformPhysicalPointToIndex((100, 0))
dose_line = dose_plane_array[:, dose_plane_array.shape[1]//2]

plt.plot(dose_plane_array[:, 256])