import vtk


def draw_bound_rect(reader, renderer):
    bounds = reader.GetOutput().GetBounds()
    # Calculate x, y, and z sizes
    x_size = bounds[1] - bounds[0]
    y_size = bounds[3] - bounds[2]
    z_size = bounds[5] - bounds[4]

    # Create a box representing the bounding box of the STL model
    box = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.InsertNextPoint(bounds[0], bounds[2], bounds[4])  # vertex 0
    points.InsertNextPoint(bounds[1], bounds[2], bounds[4])  # vertex 1
    points.InsertNextPoint(bounds[1], bounds[3], bounds[4])  # vertex 2
    points.InsertNextPoint(bounds[0], bounds[3], bounds[4])  # vertex 3
    points.InsertNextPoint(bounds[0], bounds[2], bounds[5])  # vertex 4
    points.InsertNextPoint(bounds[1], bounds[2], bounds[5])  # vertex 5
    points.InsertNextPoint(bounds[1], bounds[3], bounds[5])  # vertex 6
    points.InsertNextPoint(bounds[0], bounds[3], bounds[5])  # vertex 7

    box.SetPoints(points)

    # Create lines connecting the vertices
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(2)
    lines.InsertCellPoint(0)
    lines.InsertCellPoint(1)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(1)
    lines.InsertCellPoint(2)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(2)
    lines.InsertCellPoint(3)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(3)
    lines.InsertCellPoint(0)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(4)
    lines.InsertCellPoint(5)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(5)
    lines.InsertCellPoint(6)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(6)
    lines.InsertCellPoint(7)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(7)
    lines.InsertCellPoint(4)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(0)
    lines.InsertCellPoint(4)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(1)
    lines.InsertCellPoint(5)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(2)
    lines.InsertCellPoint(6)

    lines.InsertNextCell(2)
    lines.InsertCellPoint(3)
    lines.InsertCellPoint(7)

    box.SetLines(lines)

    # Step 3: Visualize the STL model and the box
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(box)
    else:
        mapper.SetInputData(box)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    annotation_text = add_annotations(
        renderer=renderer, x_size=x_size, y_size=y_size, z_size=z_size, box=box
    )
    return actor, annotation_text

    # Set up camera
    # renderer.GetActiveCamera().SetPosition(x_size / 2, y_size / 2, z_size * 2)
    # renderer.GetActiveCamera().SetFocalPoint(x_size / 2, y_size / 2, (z_size / 2) + bounds[4])


def add_annotations(renderer, x_size, y_size, z_size, box):
    # Initialize traversal of the lines in the box
    lines = box.GetLines()
    lines.InitTraversal()

    cell_array = vtk.vtkIdList()
    l = []
    while lines.GetNextCell(cell_array):
        annotation_text = vtk.vtkBillboardTextActor3D()
        annotation_text.GetTextProperty().SetColor(1.0, 1.0, 0)  # Yellow color
        annotation_text.GetTextProperty().SetFontSize(16)
        ptId1 = cell_array.GetId(0)
        ptId2 = cell_array.GetId(1)

        # Calculate the midpoint of the line
        mid_point = [sum(p) / 2 for p in zip(box.GetPoint(ptId1), box.GetPoint(ptId2))]

        # Determine the corresponding size based on line connectivity
        size = 0.0
        if (ptId1 == 0 and ptId2 == 1) or (ptId1 == 2 and ptId2 == 3):
            size = x_size
        elif (ptId1 == 1 and ptId2 == 2) or (ptId1 == 3 and ptId2 == 0):
            size = y_size
        elif (ptId1 == 4 and ptId2 == 5) or (ptId1 == 6 and ptId2 == 7):
            size = x_size
        elif (ptId1 == 5 and ptId2 == 6) or (ptId1 == 7 and ptId2 == 4):
            size = y_size
        elif (
            (ptId1 == 0 and ptId2 == 4)
            or (ptId1 == 1 and ptId2 == 5)
            or (ptId1 == 2 and ptId2 == 6)
            or (ptId1 == 3 and ptId2 == 7)
        ):
            size = z_size

        annotation_text.SetInput("%.2f mm" % size)
        annotation_text.SetPosition(mid_point[0], mid_point[1], mid_point[2]) 
        l.append(annotation_text)       
    return l
