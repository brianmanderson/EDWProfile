import os
import math
import matplotlib.pyplot as plt
import numpy as np
from DicomRTTool.ReaderWriter import DicomReaderWriter
from PlotScrollNumpyArrays.Plot_Scroll_Images import plot_scroll_Image
import SimpleITK as sitk


PDD = {'15X': {"Depth": [10.0191, 3.99859], "PDD": [76.6987, 96.1042]},
       '6X': {'Depth': [9.99814, 4.01534], "PDD": [69.5299, 90.9968]}}
cross_plane_field_size = 200 * .8  # in mm
physical_start = cross_plane_field_size / 2
for energy in ['15X', '6X']:
    for angle in [30, 60]:
        path = fr"K:\DosePlane\{energy}\{angle}Degree"
        file_name = f"DosePlane_{energy}_{angle}Degree.nii.gz"
        data = PDD[energy]
        u = math.log(data["PDD"][0]/data["PDD"][1])/(data["Depth"][1]-data["Depth"][0])
        if not os.path.exists(file_name) or True:
            Dicom_reader = DicomReaderWriter(verbose=False)
            Dicom_reader.walk_through_folders(path)
            Dicom_reader.get_dose()
            dose_plane = Dicom_reader.dose_handle[:, :, 0]
            sitk.WriteImage(dose_plane, file_name)
        else:
            dose_plane = sitk.ReadImage(file_name)

        plane_size = dose_plane.GetSize()
        dose_plane_array = sitk.GetArrayFromImage(dose_plane)
        physical_center = dose_plane.TransformContinuousIndexToPhysicalPoint((plane_size[0]//2, plane_size[1]//2))

        wanted_start = dose_plane.TransformPhysicalPointToIndex((physical_center[0],
                                                                 physical_center[1] - physical_start))
        wanted_stop = dose_plane.TransformPhysicalPointToIndex((physical_center[0],
                                                                physical_center[1] + physical_start))
        dose_line = dose_plane_array[wanted_start[1]:wanted_stop[1], wanted_start[0]]
        start_value = dose_line[0]*100  # in cGy
        stop_value = dose_line[-1]*100  # in cGy
        """
        Now measuring the angle
        """
        measured_angle = np.round(math.degrees(math.atan(math.log(start_value/stop_value)/(u*(physical_start*2/10)))), 2)
        above = np.round(math.degrees(math.atan(math.log(start_value*1.02/(stop_value*.98))/(u*(physical_start*2/10)))), 2)
        below = np.round(math.degrees(math.atan(math.log(start_value*0.98/(stop_value*1.02))/(u*(physical_start*2/10)))), 2)
        print(f"For {energy} and {angle} angle, we expect it to be {measured_angle} and between {below} and {above}")
