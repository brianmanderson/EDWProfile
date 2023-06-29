import os
import math
import matplotlib.pyplot as plt
import numpy as np
from Dicom_RT_and_Images_to_Mask.src.DicomRTTool.ReaderWriter import DicomReaderWriter
from PlotScrollNumpyArrays.Plot_Scroll_Images import plot_scroll_Image
import SimpleITK as sitk
from NiftiResampler.ResampleTools import ImageResampler


PDD = {'15X': {"Depth": [10.0191, 3.99859], "PDD": [76.6987, 96.1042]},
       '6X': {'Depth': [9.99814, 4.01534], "PDD": [69.5299, 90.9968]}}
energy = '6X'
path = fr"K:\DosePlane\{energy}"
cross_plane_field_size = 200*.9  # in mm
physical_start = cross_plane_field_size/2
hard_shift = 0
data = PDD[energy]
u = math.log(data["PDD"][0]/data["PDD"][1])/(data["Depth"][1]-data["Depth"][0])
if not os.path.exists(f"DosePlane_{energy}.nii.gz") or True:
    Dicom_reader = DicomReaderWriter(description='Examples', verbose=False, get_dose_output=True, Contour_Names=["Body"])
    Dicom_reader.set_contour_names_and_associations(contour_names=["Body"])
    Dicom_reader.walk_through_folders(path)
    Dicom_reader.get_images()
    Dicom_reader.get_dose()
    dose_plane = Dicom_reader.dose_handle[:, :, 0]
    sitk.WriteImage(dose_plane, f"DosePlane_{energy}.nii.gz")
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
    dose_plane = sitk.ReadImage(f"DosePlane_{energy}.nii.gz")

plane_size = dose_plane.GetSize()
dose_plane_array = sitk.GetArrayFromImage(dose_plane)
spacing = dose_plane.GetSpacing()[1]
physical_center = dose_plane.TransformContinuousIndexToPhysicalPoint((plane_size[0]//2, plane_size[1]//2))
wanted_start = dose_plane.TransformPhysicalPointToIndex((physical_center[0], physical_center[1] - physical_start))
wanted_stop = dose_plane.TransformPhysicalPointToIndex((physical_center[0], physical_center[1] + physical_start))
dose_line = dose_plane_array[wanted_start[1]:wanted_stop[1], wanted_start[0]]
start_value = dose_line[0]*100 # in cGy
stop_value = dose_line[-1]*100 # in cGy
measured_angle = math.degrees(math.atan(math.log(start_value/stop_value)/(u*(physical_start*2/10))))
above = math.degrees(math.atan(math.log(start_value*1.02/(stop_value*.98))/(u*(physical_start*2/10))))
below = math.degrees(math.atan(math.log(start_value*0.98/(stop_value*1.02))/(u*(physical_start*2/10))))
print(f"Measured angle is expected to be {measured_angle} and between {below} and {above}")
