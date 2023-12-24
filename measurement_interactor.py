import vtk
from collections import defaultdict
import math
import random
import time

class MeasurementInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtk_widget, window):
        self.window = window
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        # Register observer for the MouseMoveEvent
        self.AddObserver("MouseMoveEvent", self.on_mouse_move)
        self.vtk_widget = vtk_widget
        self.measurement_text = ""
        self.measurement_actors = defaultdict(list)
        self.measurement_start_position = None
        self.measurement_active = False
        self.scaling_factor = 1.0  # Set the scaling factor here
        self.line_actor = None  # Line actor to store the line between start and end points

        self.dynamic_line_actor = None  # Line actor for the dynamic line
        self.dynamic_line_source = None  # Line source for the dynamic line
        self.dynamic_line_color = (1.0, 0.0, 0.0)  # Color of the dynamic line (e.g., red)
        self.last_update = time.time()


    def _left_button_press_event(self, obj, event):
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


    def add_measurement_text(self, position, distance_mm, c=(1.0, 0.0, 0)):
        measurement_text = f"{distance_mm:.2f} mm"
        measurement_actor = vtk.vtkBillboardTextActor3D()
        measurement_actor.SetInput(measurement_text)
        measurement_actor.SetPosition(position[0], position[1], position[2] + 1.0)
        measurement_actor.GetTextProperty().SetColor(c)  # Green color
        measurement_actor.GetTextProperty().SetFontSize(16)  # Adjust font size as needed
        measurement_actor.SetVisibility(True)

        self.measurement_actors[(position, distance_mm)].append(measurement_actor)

        self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(
            measurement_actor
        )

    def random_color(self):
        # Generate random RGB values
        r = random.uniform(0.0, 1.0)
        g = random.uniform(0.0, 1.0)
        b = random.uniform(0.0, 1.0)
        return (r, g, b)

    def _add_saphere(self, start_position, end_position):
        # Create spheres at the start and end positions
        sphere_radius = .080  # Adjust the radius as needed
        start_sphere = vtk.vtkSphereSource()
        start_sphere.SetRadius(sphere_radius)
        start_sphere.SetCenter(start_position)

        end_sphere = vtk.vtkSphereSource()
        end_sphere.SetRadius(sphere_radius)
        end_sphere.SetCenter(end_position)

        # Create mappers and actors for the spheres
        start_sphere_mapper = vtk.vtkPolyDataMapper()
        start_sphere_mapper.SetInputConnection(start_sphere.GetOutputPort())
        start_sphere_actor = vtk.vtkActor()
        start_sphere_actor.SetMapper(start_sphere_mapper)

        end_sphere_mapper = vtk.vtkPolyDataMapper()
        end_sphere_mapper.SetInputConnection(end_sphere.GetOutputPort())
        end_sphere_actor = vtk.vtkActor()
        end_sphere_actor.SetMapper(end_sphere_mapper)

        # Set colors for the spheres (you can customize these)
        start_sphere_actor.GetProperty().SetColor(0.0, 1.0, 0.0)  # Green color
        end_sphere_actor.GetProperty().SetColor(0.0, 1.0, 0.0)  # Green color

        # Add the line and sphere actors to the renderer
        renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()

        renderer.AddActor(start_sphere_actor)
        renderer.AddActor(end_sphere_actor)

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

    def handle_measurement(self, position):
        if not self.measurement_active:
            self.measurement_start_position = position
            self.measurement_active = True                           
          
        else:
            distance_mm = self.calculate_distance(
                self.measurement_start_position, position
            )
            midpoint = (
                (self.measurement_start_position[0] + position[0]) / 2,
                (self.measurement_start_position[1] + position[1]) / 2,
                 position[2],
            )
            self.add_measurement_text(midpoint, distance_mm)
            self.measurement_active = False

        c = self.random_color()
            
        self.draw_line_with_points(self.measurement_start_position, position, c)

    def draw_line_with_points(self, start_position, end_position, c):
        self._add_saphere(start_position, end_position)
        # Create a line source for the dynamic line
        self.dynamic_line_source = vtk.vtkLineSource()
        self.dynamic_line_source.SetPoint1(start_position)
        self.dynamic_line_source.SetPoint2(end_position)
        self.dynamic_line_source.Update()

        # Create a mapper and actor for the dynamic line
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.dynamic_line_source.GetOutput())

        self.dynamic_line_actor = vtk.vtkActor()
        self.dynamic_line_actor.SetMapper(mapper)
        self.dynamic_line_actor.GetProperty().SetColor(self.dynamic_line_color)
        self.dynamic_line_actor.GetProperty().SetLineWidth(2)

        # Add the dynamic line actor to the renderer
        renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        renderer.AddActor(self.dynamic_line_actor)

        # Render the scene
        self.vtk_widget.GetRenderWindow().Render()
    def on_mouse_move(self, obj, event):
        if time.time() - self.last_update < 0.1:
            return
        self.last_update = time.time()

        if self.measurement_active and self.dynamic_line_source:
            interactor = self.GetInteractor()
            mouse_position = interactor.GetEventPosition()
            picker = vtk.vtkCellPicker()
            picker.Pick(
                mouse_position[0],
                mouse_position[1],
                0,
                self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer(),
            )
            if picker.GetCellId() >= 0:
                end_position = picker.GetPickPosition()
                # Update the endpoint of the dynamic line
                self.dynamic_line_source.SetPoint1(self.measurement_start_position)
                self.dynamic_line_source.SetPoint2(end_position)
                self.dynamic_line_source.Update()
                self.vtk_widget.GetRenderWindow().Render() 
 