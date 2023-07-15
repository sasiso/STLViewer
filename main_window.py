import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5.QtWidgets import QTextEdit
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import yellow
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtGui import QPixmap
from annotation_interactor import AnnotationInteractorStyle

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Express CAD Service Viewer")

        # Create a VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        # Create an instance of AnnotationInteractorStyle
        self.annotation_interactor_style = AnnotationInteractorStyle(self.vtk_widget, self)
        # Create a tool pane widget
        self.tool_pane = QtWidgets.QWidget(self)
        self.tool_pane.setMaximumWidth(
            int(0.2 * self.width())
        )  # Set maximum width to 20% of window width

        # Create a slider widget
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.tool_pane)
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
        self.switch_button = QtWidgets.QPushButton("Wireframe", self.tool_pane)
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

        # Create the layout for the tool pane
        tool_layout = QtWidgets.QVBoxLayout(self.tool_pane)
        tool_layout.addWidget(self.slider)
        tool_layout.addWidget(self.switch_button)
        tool_layout.addStretch()
        
        self.progress_bar = QProgressBar(self.tool_pane)
        

        tool_layout.addWidget(self.progress_bar)

        # Create the main layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.vtk_widget)
        main_layout.addWidget(self.tool_pane)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create a frame and set the main layout
        frame = QtWidgets.QFrame(self)
        frame.setLayout(main_layout)

        # Set the central widget
        self.setCentralWidget(frame)

        # Initialize VTK objects and rendering
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Load and render the STL file
        self.load_stl_file("path_to_stl_file.stl")

        # Connect the slider value change event
        self.slider.valueChanged.connect(self.on_slider_value_changed)

        # Connect the switch button clicked event
        self.switch_button.clicked.connect(self.on_switch_button_clicked)

        # Create a timer to delay the update
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(500)  # Adjust the delay as needed
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_model)

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

        # Create the annotation mode toggle button
        self.annotation_button = QtWidgets.QPushButton(
            "Annotation Mode", self.tool_pane
        )
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

        # Add the annotation button to the tool pane layout
        tool_layout.addWidget(self.annotation_button)

        # Create an annotation text edit widget
        self.annotation_text_edit = QTextEdit(self.tool_pane)
        self.annotation_text_edit.setPlaceholderText("Add annotation...")
        self.annotation_text_edit.setEnabled(False)
        self.annotation_text_edit.setStyleSheet(
            "QTextEdit {" "border: 1px solid gray;" "border-radius: 5px;" "}"
        )

        # Add the annotation text edit widget to the tool pane layout
        tool_layout.addWidget(self.annotation_text_edit)

        # ... existing code ...

        # Connect the annotation button clicked event
        self.annotation_button.clicked.connect(self.on_annotation_button_clicked)
        self.progress_bar.setValue(0)
        self.initialize_progress_bar()

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

            renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()

            pdf.add_page()

            # Define the dimensions and positions for each image in the 2x2 layout
            image_width = 297 / 2  # Half the width of the page
            image_height = 210 / 2  # Half the height of the page
            image_positions = [
                (0, 0),  # Top-left position (bottom view)
                (image_width, 0),  # Top-right position (top view)
                (0, image_height),  # Bottom-left position (right view)
                (image_width, image_height)  # Bottom-right position (left view)
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
            self.interactor.SetInteractorStyle(
                self.annotation_interactor_style
            )
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

