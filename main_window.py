import vtk
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction, QFileDialog
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QProgressBar
import measurement_interactor
from annotation_interactor import AnnotationInteractorStyle
from custom_pdf import CustomPDF
from drawing_interactor import DrawingInteractorStyle

from vtk.util import numpy_support
import numpy
import cv2
import os


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Express CAD Service Viewer")

        # Create a temporary folder to store images
        self.temp_folder = "temp_images"
        os.makedirs(self.temp_folder, exist_ok=True)

        # Create a VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        # Initialize VTK objects and rendering
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Load and render the STL file
        #self.load_stl_file("path_to_stl_file.stl")

        # Create a tool pane widget
        self.tool_pane = QtWidgets.QWidget(self)
        self.tool_pane.setMaximumWidth(
            int(0.4 * self.width())
        )  # Set maximum width to 20% of window width

        # Group the buttons in a box layout
        button_layout = QtWidgets.QVBoxLayout()

        # Create a slider widget
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setStyleSheet(
            "QSlider::handle:horizontal {"
            "background-color: #2196F3;"
            "border: 1px solid #2196F3;"
            "width: 10px;"
            "margin: -5px 0;"
            "border-radius: 5px;"
            "}"
        )

        # Create a wireframe switch button
        self.switch_button = QtWidgets.QPushButton("Wireframe")
        self.switch_button.setCheckable(True)
        self.switch_button.setStyleSheet(
            "QPushButton {"
            "background-color: #4CAF50;"
            "border: none;"
            "padding: 5px 10px;"
            "border-radius: 5px;"
            "color: white;"
            "}"
            "QPushButton:checked {"
            "background-color: #F44336;"
            "}"
        )

        # Create the annotation mode toggle button
        self.annotation_button = QtWidgets.QPushButton("Annotation Mode")
        self.annotation_button.setCheckable(True)
        self.annotation_button.setStyleSheet(
            "QPushButton {"
            "background-color: #2196F3;"
            "border: none;"
            "padding: 5px 10px;"
            "border-radius: 5px;"
            "color: white;"
            "}"
            "QPushButton:checked {"
            "background-color: #F44336;"
            "}"
        )

        # Create a measurement mode toggle button
        self.measurement_button = QtWidgets.QPushButton("Measurement Mode")
        self.measurement_button.setCheckable(True)
        self.measurement_button.setStyleSheet(
            "QPushButton {"
            "background-color: #2196F3;"
            "border: none;"
            "padding: 5px 10px;"
            "border-radius: 5px;"
            "color: white;"
            "}"
            "QPushButton:checked {"
            "background-color: #F44336;"
            "}"
        )

        # Create the drawing mode toggle button
        self.drawing_button = QtWidgets.QPushButton("Drawing Mode")
        self.drawing_button.setCheckable(True)
        self.drawing_button.setStyleSheet(
            "QPushButton {"
            "background-color: #2196F3;"
            "border: none;"
            "padding: 5px 10px;"
            "border-radius: 5px;"
            "color: white;"
            "}"
            "QPushButton:checked {"
            "background-color: #F44336;"
            "}"
        )

        # Create the annotation text edit widget
        self.annotation_text_edit = QtWidgets.QTextEdit(self.tool_pane)
        self.annotation_text_edit.setPlaceholderText("Add annotation...")
        self.annotation_text_edit.setEnabled(False)
        self.annotation_text_edit.setStyleSheet(
            "QTextEdit {" "border: 1px solid gray;" "border-radius: 5px;" "}"
        )
        self.progress_bar = QProgressBar(self.tool_pane)
        # Add buttons to the button layout
        button_layout.addWidget(self.slider)
        button_layout.addWidget(self.switch_button)

        button_layout.addWidget(self.measurement_button)
        button_layout.addWidget(self.drawing_button)
        button_layout.addWidget(self.annotation_button)
        button_layout.addWidget(self.annotation_text_edit)
        button_layout.addWidget(self.progress_bar)
        button_layout.addStretch()

        # Set the layout for the tool pane
        self.tool_pane.setLayout(button_layout)
        

        # Create a frame to hold the VTK widget and tool pane
        frame = QtWidgets.QFrame(self)
        main_layout = QtWidgets.QHBoxLayout(frame)
        main_layout.addWidget(self.vtk_widget)
        main_layout.addWidget(self.tool_pane)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Set the central widget
        self.setCentralWidget(frame)

        # Connect the slider value change event
        self.slider.valueChanged.connect(self.on_slider_value_changed)

        # Connect the switch button clicked event
        self.switch_button.clicked.connect(self.on_switch_button_clicked)

        # Connect the annotation button clicked event
        self.annotation_button.clicked.connect(self.on_annotation_button_clicked)

        # Connect the measurement button clicked event
        self.measurement_button.clicked.connect(self.on_measurement_button_clicked)

        # Connect the drawing button clicked event
        self.drawing_button.clicked.connect(self.on_drawing_button_clicked)

        # Connect the measurement button clicked event
        self.measurement_button.clicked.connect(self.on_measurement_button_clicked)        

        # Create a File menu
        file_menu = self.menuBar().addMenu("File")

        # Create an Open action in the File menu
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_pdf_action = QAction("Save PDF", self)
        save_pdf_action.setShortcut("Ctrl+S")
        save_pdf_action.triggered.connect(self.save_pdf_dialog)
        file_menu.addAction(save_pdf_action)


        # Create a button to record video
        self.record_button = QtWidgets.QPushButton("Record Video")
        self.record_button.clicked.connect(self.record_video)
        button_layout.addWidget(self.record_button)

        # Create a timer to delay the update
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(500)  # Adjust the delay as needed
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_model)

        
        self.setup_interectors()

        # Set up the gold material for the model
        self.set_gold_material()

        # Initialize video recording variables
        self.video_writer = None
        self.frames = []  # Store frames for video

    def set_gold_material(self):
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextItem()
        while actor:
            # Set the actor's color to 22 K gold
            actor.GetProperty().SetColor(0.91, 0.76, 0.29)  # RGB values for gold
            actor.GetProperty().SetSpecular(0.5)
            actor.GetProperty().SetSpecularPower(30)
            actor.GetProperty().SetAmbient(0.2)
            actor.GetProperty().SetDiffuse(0.8)
            actor = actors.GetNextItem()

        # Reset the camera after changing the model color
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def record_video(self):
        # Add a timer to control the rotation for video recording
        self.rotation_timer = QtCore.QTimer()
        self.rotation_timer.timeout.connect(self.rotate_for_video)
        self.rotation_angle = 0  # Initial angle for rotation
        self.counter = 0
        self.rotation_timer.start(30)  # Adjust the interval as needed
        
   #--
    def capture_current_view(self):
        # Capture the current frame
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(self.vtk_widget.GetRenderWindow())
        window_to_image_filter.Update()
        vtk_image = window_to_image_filter.GetOutput()

        # Use vtk's functionality to convert the image to a numpy array
        vtk_array = vtk_image.GetPointData().GetScalars()
        components = vtk_array.GetNumberOfComponents()
        height, width, _ = vtk_image.GetDimensions()
        
        # Convert VTK array to NumPy array
        img = numpy_support.vtk_to_numpy(vtk_array).reshape(height, width, components)

        # Ensure that the image has 3 color channels (RGB)
        if components == 1:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif components == 2:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR5652RGB)
        elif components == 3:
            img_rgb = img
        elif components == 4:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        else:
            raise ValueError(f"Unsupported number of image components: {components}")

        # Save the frame as an image in the temporary folder
        image_path = os.path.join(self.temp_folder, f"frame_{self.rotation_angle}.png")
        cv2.imwrite(image_path, cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
   #--
    
    def rotate_for_video(self):
        # Rotate the camera for video recording
        renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        camera.Azimuth(2)  # Adjust the rotation angle as needed
        self.rotation_angle += 2
                # Append the frame to the video writer
        self.counter +=1
        spacer = ''
        if self.counter < 10:
            spacer = '00'
        elif self.counter < 100:
            spacer = '0'

        
        image_path = os.path.join(self.temp_folder, f"frame_{spacer}{self.counter}.png")

        self.save_current_view_as_image(image_path=image_path)


               

        # Stop recording after 10 seconds (adjust as needed)
        if self.rotation_angle >= 350:  # 10 seconds at 30 fps
            import video_capture
            self.rotation_timer.stop()
            video_capture.encode()



            
    def setup_interectors(self):
        # Create an instance of AnnotationInteractorStyle
        self.annotation_interactor_style = AnnotationInteractorStyle(
            self.vtk_widget, self
        )
        # Create a DrawingInteractorStyle instance
        self.drawing_interactor_style = DrawingInteractorStyle(self.vtk_widget, self)

        # Create an instance of MeasurementInteractorStyle
        self.measurement_interactor_style = (
            measurement_interactor.MeasurementInteractorStyle(self.vtk_widget, self)
        )

    def update_progress(self, value):
        self.progress_bar.setValue(int(value))

    def save_pdf_dialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)"
        )

        if file_path:
            self.save_pdf_with_annotations(file_path)

    def save_current_view_as_image(self, image_path):
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(self.vtk_widget.GetRenderWindow())
        window_to_image_filter.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(image_path)
        writer.SetInputData(window_to_image_filter.GetOutput())
        writer.Write()

    def initialize_progress_bar(self):
        self.progress_bar.setRange(0, 100)

    def rotate_camera(self):
        renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        camera.Azimuth(90)
        self.vtk_widget.GetRenderWindow().Render()

    def save_pdf_with_annotations(self, file_path):
        try:
            pdf = CustomPDF(orientation="L", unit="mm", format="A4")
            pdf.set_auto_page_break(auto=True, margin=15)

            renderer = (
                self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
            )

            pdf.add_page()

            # Define the dimensions and positions for each image in the 2x2 layout
            image_width = 297 / 2  # Half the width of the page
            image_height = 210 / 2  # Half the height of the page
            image_positions = [
                (0, 0),  # Top-left position (bottom view)
                (image_width, 0),  # Top-right position (top view)
                (0, image_height),  # Bottom-left position (right view)
                (image_width, image_height),  # Bottom-right position (left view)
            ]

            image_index = 0
            total_images = 4
            for image_index in range(total_images):
                # Save the current view as an image
                image_path = f"temp_image_{image_index}.png"
                if image_index == 0:  # Bottom view
                    self.rotate_camera()  # Rotate the camera for bottom view
                elif image_index == 1:  # Top view
                    self.rotate_camera()  # Rotate the camera again for top view
                elif image_index == 2:  # Right view
                    self.rotate_camera()  # Rotate the camera again for right view
                elif image_index == 3:  # Left view
                    self.rotate_camera()  # Rotate the camera again for left view

                self.save_current_view_as_image(image_path)

                # Add the image to the PDF at the corresponding position
                x, y = image_positions[image_index]

                # Load the saved image
                image = QPixmap(image_path)
                image_width_px = image.width()
                image_height_px = image.height()

                # Calculate the scaling factors
                scale_width = image_width / image_width_px
                scale_height = image_height / image_height_px

                # Calculate the scaled dimensions
                scaled_width = image_width_px * scale_width
                scaled_height = image_height_px * scale_height

                # Add the scaled image to the PDF
                pdf.image(image_path, x=x, y=y, w=scaled_width, h=scaled_height)

                # Update the progress bar
                progress_value = (image_index + 1) * 100 / total_images
                self.update_progress(progress_value)
            pdf.output(file_path)
        except Exception as ex:
            print(ex)

    def on_annotation_button_clicked(self):
        if self.annotation_button.isChecked():
            self.annotation_text_edit.setEnabled(True)
            self.interactor.SetInteractorStyle(self.annotation_interactor_style)
        else:
            self.annotation_text_edit.setEnabled(False)
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    def open_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open STL File", "", "STL Files (*.stl)"
        )

        if file_path:
            self.load_stl_file(file_path)
            self.set_gold_material()

    def load_stl_file(self, file_path):
        # Remove existing actors from the renderer
        self.renderer.RemoveAllViewProps()

        # Create a reader and load the STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()

        # Get the STL mesh
        stl_mesh = reader.GetOutput()

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(stl_mesh)

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Add the actor to the renderer
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def on_slider_value_changed(self, value):
        # Restart the update timer
        self.update_timer.start()

    def on_switch_button_clicked(self):
        # Restart the update timer
        self.update_timer.start()

    def update_model(self):
        # This function is called after adjusting the camera position
        opacity = self.slider.value() / 100.0
        is_wireframe = self.switch_button.isChecked()
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextItem()
        while actor:
            actor.GetProperty().SetOpacity(opacity)
            if is_wireframe:
                actor.GetProperty().SetRepresentationToWireframe()
            else:
                actor.GetProperty().SetRepresentationToSurface()
            actor = actors.GetNextItem()
        self.vtk_widget.GetRenderWindow().Render()

        # Capture the current view and save it as an image
        self.capture_current_view()

    def on_measurement_button_clicked(self):
        if self.measurement_button.isChecked():
            self.interactor.SetInteractorStyle(self.measurement_interactor_style)
            self.annotation_button.setEnabled(False)
        else:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
            self.annotation_button.setEnabled(True)

    def on_drawing_button_clicked(self):
        if self.drawing_button.isChecked():
            self.interactor.SetInteractorStyle(self.drawing_interactor_style)
        else:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
