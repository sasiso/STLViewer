import vtk
from collections import defaultdict
import math

class MeasurementInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtk_widget, window):
        self.window = window
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.vtk_widget = vtk_widget
        self.measurement_text = ""
        self.measurement_actors = defaultdict(list)
        self.measurement_start_position = None
        self.measurement_active = False
        self.scaling_factor = 1.0  # Set the scaling factor here
        self.line_actor = None  # Line actor to store the line between start and end points


    def left_button_press_event(self, obj, event):
        if not self.window.measurement_button.isChecked():
            super().OnLeftButtonDown()
            return

        interactor = self.GetInteractor()
        mouse_position = interactor.GetEventPosition()

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.001)
        picker.Pick(
            mouse_position[0],
            mouse_position[1],
            0,
            self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer(),
        )

        if picker.GetCellId() >= 0:
            picked_position = picker.GetPickPosition()
            self.handle_measurement(picked_position)

        self.vtk_widget.GetRenderWindow().Render()

    def handle_measurement(self, position):
        if not self.measurement_active:
            self.measurement_start_position = position
            self.measurement_active = True
        else:
            self.measurement_active = False
            distance_mm = self.calculate_distance(
                self.measurement_start_position, position
            )
            self.add_measurement_text(position, distance_mm)
            self.draw_line(self.measurement_start_position, position)

    def draw_line(self, start_position, end_position):
        # Create a line between the start and end position
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(start_position)
        line_source.SetPoint2(end_position)
        line_source.Update()

        # Create a mapper and actor for the line
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(line_source.GetOutput())

        self.line_actor = vtk.vtkActor()
        self.line_actor.SetMapper(mapper)
        self.line_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red color
        self.line_actor.GetProperty().SetLineWidth(2)  # Adjust line width as needed

        # Add the line actor to the renderer
        self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.line_actor)
        self.vtk_widget.GetRenderWindow().Render()


    def calculate_distance(self, start_position, end_position):
        # Calculate the distance between two points in millimeters
        squared_distance = vtk.vtkMath.Distance2BetweenPoints(
            start_position, end_position
        )
        distance_mm = math.sqrt(squared_distance) * self.scaling_factor  # Adjust scaling_factor
        return round(distance_mm, 2)


    def add_measurement_text(self, position, distance_mm):
        measurement_text = f"{distance_mm:.2f} mm"
        measurement_actor = vtk.vtkBillboardTextActor3D()
        measurement_actor.SetInput(measurement_text)
        measurement_actor.SetPosition(position)
        measurement_actor.GetTextProperty().SetColor(0.0, 1.0, 0.0)  # Green color
        measurement_actor.GetTextProperty().SetFontSize(20)  # Adjust font size as needed
        measurement_actor.SetVisibility(True)

        self.measurement_actors[(position, distance_mm)].append(measurement_actor)

        self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(
            measurement_actor
        )
