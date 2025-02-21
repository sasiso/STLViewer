import vtk
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction, QFileDialog
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QProgressBar
import os
from bound_rect import draw_bound_rect

from weight import get_weight_text
from PyQt5.QtWidgets import QCheckBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(
            "Express CAD Service Viewer - Beta v2.0.0 support: expresscadservice@gmail.com"
        )
        self.setFixedSize(1200, 800)
        self.rectangle_actor = None
        self.size_annotation_text = None
        self._image_actor = None
        self.reader = None

        # Create a temporary folder to store images
        self.temp_folder = "temp_images"
        os.makedirs(self.temp_folder, exist_ok=True)
        self.file_path = None

        # Additional variables for color and rotation
        self.color_index = 0
        self.colors = [
            (0.91, 0.76, 0.29),  # 18K gold
            (0.98, 0.84, 0.65),  # 14K gold
            (0.81, 0.71, 0.23),  # 9K gold
            (0.75, 0.75, 0.75),  # Silver
            (0.68, 0.68, 0.68),  # Platinum
            (0.86, 0.58, 0.58),  # Rose gold
        ]
        self.color_index = 0
        self.metal_color = (0.91, 0.76, 0.29)

        # Create a VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        # Initialize VTK objects and rendering
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        # Connect the keypress event
        self.interactor.AddObserver("KeyPressEvent", self.on_key_press)
        # Load and render the STL file
        # self.load_stl_file("path_to_stl_file.stl")

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
        self.annotation_text_edit.setPlaceholderText(
            "Click annotion button, add text here and click on model"
        )  # Set your watermark hint

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

        # Add text actor to the renderer
        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetTextScaleModeToNone()
        self.text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.text_actor.SetPosition(0.8, 0.8)  # Adjust the position as needed
        self.text_actor.GetTextProperty().SetColor(0.0, 0.0, 1.0)  # Blue color
        self.text_actor.GetTextProperty().SetFontSize(20)
        self.renderer.AddActor(self.text_actor)

        # Create a text actor for the watermark
        self.watermark_actor = vtk.vtkTextActor()
        self.watermark_actor.SetTextScaleModeToNone()
        self.watermark_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.watermark_actor.SetPosition(0.05, 0.02)  # Adjust the position as needed
        self.watermark_actor.GetTextProperty().SetColor(0.5, 0.5, 0.5)  # Gray color
        self.watermark_actor.GetTextProperty().SetFontSize(20)

        # Create an actor for the logo overlay
        self.logo_actor = vtk.vtkActor2D()

        self._add_logo()

        self.renderer.AddActor(self.watermark_actor)

        # Create a button to record video
        self.record_button = QtWidgets.QPushButton("Record Video")
        self.record_button.clicked.connect(self.record_video)
        button_layout.addWidget(self.record_button)

        # Create a checkbox for video recording
        self.video_recording_checkbox = QCheckBox(
            "Interactive recording", self.tool_pane
        )
        button_layout.addWidget(self.video_recording_checkbox)

        # Create a progress bar for video recording
        self.video_progress_bar = QProgressBar(self.tool_pane)
        button_layout.addWidget(self.video_progress_bar)
        self.video_progress_bar.setVisible(False)
        self.video_progress_bar.setRange(0, 100)

        # Create a checkbox for draw rectangle
        self.draw_rect_checkbox = QCheckBox("Display Size", self.tool_pane)
        self.draw_rect_checkbox.setChecked(True)
        self.draw_rect_checkbox.stateChanged.connect(self.on_draw_rect_checkbox_changed)
        button_layout.addWidget(self.draw_rect_checkbox)

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
        self.vtk_widget.GetRenderWindow().Render()

    def add_annoation_actor(self, remove=False):
        if remove:
            for a in self.size_annotation_text:
                self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(
                    a
                )
            self.size_annotation_text = None
        else:
            for a in self.size_annotation_text:
                self.renderer.AddActor(a)

    def _add_logo(self):
        # Paths for branding.txt and logo.png
        branding_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "branding.txt"
        )
        logo_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logo.png"
        )

        # Read branding text (First 3 lines from branding.txt or default text)
        if os.path.exists(branding_file_path):
            with open(branding_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()[:3]
                text = "".join(lines).strip()
        else:
            text = "Express CAD Service\nWhatsApp: +61-410168567\nEmail: expresscadservice@gmail.com"

        # Set watermark text
        self.watermark_actor.SetInput(text)

        # Load and process the logo if it exists
        if os.path.exists(logo_file_path):
            logo_reader = vtk.vtkPNGReader()
            logo_reader.SetFileName(logo_file_path)
            logo_reader.Update()

            if logo_reader.GetOutput().GetScalarType() == 0:
                print("Error: Failed to read logo file. Ensure it is a valid PNG.")
                return

            # Get original image dimensions
            original_width, original_height, _ = logo_reader.GetOutput().GetDimensions()

            # Define new width and maintain aspect ratio
            new_width = 100  # Resize width in pixels
            aspect_ratio = original_height / original_width
            new_height = int(new_width * aspect_ratio)

            # Use vtkImageResize for better scaling
            resize = vtk.vtkImageResize()
            resize.SetInputConnection(logo_reader.GetOutputPort())
            resize.SetOutputDimensions(new_width, new_height, 1)
            resize.Update()

            # Use vtkImageMapper for overlay (ensures it remains on screen)
            image_mapper = vtk.vtkImageMapper()
            image_mapper.SetInputConnection(resize.GetOutputPort())
            image_mapper.SetColorWindow(255)  # Adjust contrast
            image_mapper.SetColorLevel(127.5)  # Adjust brightness

            self.logo_actor.SetMapper(image_mapper)

            # Position the logo in viewport coordinates (Bottom-left, just above text)
            position = self.logo_actor.GetPositionCoordinate()
            position.SetCoordinateSystemToNormalizedViewport()  # Screen space
            position.SetValue(0.05, 0.15)  # X, Y position (Bottom-left above text)

            # Add the logo as an overlay (Always on top)
            self.renderer.AddActor2D(self.logo_actor)

    def on_draw_rect_checkbox_changed(self, state):
        if self.rectangle_actor is None:
            return

        self.draw_rect = state == QtCore.Qt.Checked
        if not self.draw_rect:
            self.renderer.RemoveActor(self.rectangle_actor)
            # Remove text annotation if checkbox is unchecked
            self.remove_annotations()
        else:
            self._handle_size_annotations()
            self.vtk_widget.GetRenderWindow().Render()

    def remove_annotations(self):
        self.add_annoation_actor(remove=True)
        self.vtk_widget.GetRenderWindow().Render()

    def on_key_press(self, obj, event):
        key = self.interactor.GetKeySym()

        if key == "Down":
            # Increment the color index
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.set_gold_material()

        if key == "Escape":
            self._handle_buttons_states()

    def set_gold_material(self):
        actor = self._image_actor
        if actor is None:
            return

        # Set the actor's color to 22 K gold
        actor.GetProperty().SetColor(
            self.colors[self.color_index]
        )  # RGB values for gold
        actor.GetProperty().SetSpecular(1.0)
        actor.GetProperty().SetSpecularPower(50)
        actor.GetProperty().SetAmbient(0.2)
        actor.GetProperty().SetDiffuse(0.8)

        # Enable backface culling
        actor.GetProperty().BackfaceCullingOn()

        # Reset the camera after changing the model color
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def record_video(self):
        self.record_button.setEnabled(False)
        # Add a timer to control the rotation for video recording
        self.video_progress_bar.setVisible(True)
        self.remove_png_files(self.temp_folder)
        self.rotation_timer = QtCore.QTimer()
        self.rotation_timer.timeout.connect(self.rotate_for_video)
        self.rotation_angle = 0  # Initial angle for rotation
        self.counter = 0
        self.rotation_timer.start(10)  # Adjust the interval as needed

    # --
    def capture_current_view(self):
        from vtk.util import numpy_support
        import cv2

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

    # --

    def rotate_for_video(self):
        # Rotate the camera for video recording
        renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        speed = 3
        if not self.video_recording_checkbox.isChecked():
            if self.rotation_angle < 359:
                # Rotate around Y-axis
                camera.Azimuth(speed)  # Adjust the rotation angle as needed

            else:
                # Rotate around X-axis
                camera.OrthogonalizeViewUp()
                camera.Elevation(speed)

        if self.video_recording_checkbox.isChecked():
            self.rotation_angle += 2
        else:
            self.rotation_angle += speed

        # Append the frame to the video writer
        self.counter += 1
        spacer = ""
        if self.counter < 10:
            spacer = "00"
        elif self.counter < 100:
            spacer = "0"

        image_path = os.path.join(self.temp_folder, f"frame_{spacer}{self.counter}.png")
        self.save_current_view_as_image(image_path=image_path)
        val = int((self.rotation_angle / (359 * 2)) * 100)
        self.video_progress_bar.setValue(val)

        # Stop recording after 10 seconds (adjust as needed)
        if self.rotation_angle >= 359 * 2:  # 10 seconds at 30 fps
            import video_capture

            self.rotation_timer.stop()
            file_name_without_extension, file_extension = os.path.splitext(
                os.path.basename(self.file_path)
            )

            video_capture.encode(file_name_without_extension + ".mp4")
            self.video_progress_bar.setVisible(False)
            self.record_button.setEnabled(True)

    def remove_png_files(self, folder_path):
        try:
            # List all files in the folder
            files = os.listdir(folder_path)

            # Iterate through the files
            for file in files:
                # Check if the file is a .png file
                if file.endswith(".png"):
                    # Construct the full file path
                    file_path = os.path.join(folder_path, file)

                    # Remove the file
                    os.remove(file_path)
                    print(f"Removed: {file_path}")

            print("All .png files removed successfully.")

        except Exception as e:
            print(f"Error: {e}")

    def setup_interectors(self):
        from annotation_interactor import AnnotationInteractorStyle
        from drawing_interactor import DrawingInteractorStyle
        import measurement_interactor

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
        # Get the render window
        render_window = self.vtk_widget.GetRenderWindow()

        # Get the current size of the render window
        width, height = render_window.GetSize()

        # Ensure width and height are divisible by 2
        if width % 2 != 0:
            width -= 1
        if height % 2 != 0:
            height -= 1

        # Set the adjusted size back to the render window
        render_window.SetSize(width, height)
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
        from custom_pdf import CustomPDF

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
            self._handle_buttons_states(annotate=True)
            self.annotation_text_edit.setEnabled(True)
            self.interactor.SetInteractorStyle(self.annotation_interactor_style)
        else:
            self.annotation_text_edit.setEnabled(False)
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    def open_file(self):
        file_dialog = QFileDialog()
        self.file_path, _ = file_dialog.getOpenFileName(
            self, "Open STL File", "", "STL Files (*.stl)"
        )

        if self.file_path:
            if True:
                w = get_weight_text(self.file_path)
                text = ""
                for key, value in w.items():
                    text += key + ": {:.2f}".format(value) + "\n"

                self.text_actor.SetInput(text)
            self.load_stl_file(self.file_path)
            self.set_gold_material()

    def _handle_size_annotations(self):
        self.rectangle_actor, self.size_annotation_text = draw_bound_rect(
            self.reader, self.renderer
        )
        self.renderer.AddActor(self.rectangle_actor)
        self.add_annoation_actor()
        self.draw_rect_checkbox.setChecked(True)

    def load_stl_file(self, file_path):
        # Remove existing actors from the renderer
        self.renderer.RemoveAllViewProps()

        # Create a reader and load the STL file
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(file_path)
        self.reader.Update()

        # Get the STL mesh
        stl_mesh = self.reader.GetOutput()

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(stl_mesh)

        # Create an actor
        self._image_actor = vtk.vtkActor()
        self._image_actor.SetMapper(mapper)

        # Add the actor to the renderer
        self.renderer.AddActor(self._image_actor)
        self.renderer.AddActor(self.text_actor)
        self.renderer.AddActor(self.watermark_actor)
        self.renderer.AddActor(self.logo_actor)
        self._handle_size_annotations()
        self.renderer.ResetCamera()

        self.vtk_widget.GetRenderWindow().Render()

    def on_slider_value_changed(self, value):
        # Restart the update timer
        self.update_timer.start()

    def on_switch_button_clicked(self):
        # Restart the update timer
        self.update_timer.start()
        if self.switch_button.isChecked():
            self._handle_buttons_states(wireframe=True)

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

    def on_measurement_button_clicked(self):
        if self.measurement_button.isChecked():
            self._handle_buttons_states(measurement=True)
            self.interactor.SetInteractorStyle(self.measurement_interactor_style)
        else:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    def _handle_buttons_states(
        self, drawing=False, measurement=False, wireframe=False, annotate=False
    ):
        self.drawing_button.setChecked(drawing)
        self.measurement_button.setChecked(measurement)
        self.switch_button.setChecked(wireframe)
        self.annotation_button.setChecked(annotate)
        if not drawing and not measurement and not wireframe and not annotate:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    def on_drawing_button_clicked(self):
        if self.drawing_button.isChecked():
            self._handle_buttons_states(drawing=True)
            self.interactor.SetInteractorStyle(self.drawing_interactor_style)

        else:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
