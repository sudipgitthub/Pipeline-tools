import hou
from PySide2 import QtWidgets, QtCore, QtGui
import re

class SelectedNodesUI(QtWidgets.QWidget):
    def __init__(self):
        super(SelectedNodesUI, self).__init__()

        # Add this line to set the window always on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        self.setWindowTitle("Selected Nodes")
        self.setGeometry(750, 350, 320, 450)  # Increased width for Elements and Version

        # Set dark style sheet with rounded corners
        dark_stylesheet = """
        QWidget {
            background-color: #222222;
            color: #E0E0E0;
            border-radius: 5px; /* Rounded corners */
        }
        QListWidget, QComboBox {
            background-color: #111111;
            color: #ffffff;
            selection-background-color: #006400; /* Change selection color to dark green */
            border-radius: 5px; /* Rounded corners */
        }
        QPushButton {
            background-color: #111111;
            color: #ffffff;
            border: 1px solid #000000;
            border-radius: 5px; /* Rounded corners */
            outline: none;
        }
        QPushButton:hover {
            background-color: #015001;
            color: #ffffff;
            border: 1px solid #015001;
            border-radius: 5px; /* Rounded corners */
        }
        QPushButton:pressed {
            background-color: #339933;
            color: #ffffff;
            border: 1px solid #339933;
            border-radius: 5px; /* Rounded corners */
        }
        QLabel {
            color: #ffffff;
            font-weight: normal; /* Make the text bold */
        }
        """

        self.setStyleSheet(dark_stylesheet)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Selected nodes list
        self.nodes_list = QtWidgets.QListWidget()
        self.nodes_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.layout.addWidget(self.nodes_list)

        # Connect list selection changed signal
        self.nodes_list.itemSelectionChanged.connect(self.update_selected_nodes_label)

        # Horizontal layout for frame inputs
        frame_layout = QtWidgets.QHBoxLayout()

        # Frame range inputs
        self.start_frame_edit = QtWidgets.QLineEdit()
        self.start_frame_edit.setText(str(hou.playbar.playbackRange()[0]))  # Set default to current start frame
        frame_layout.addWidget(QtWidgets.QLabel("Start Frame:"))
        frame_layout.addWidget(self.start_frame_edit)

        self.end_frame_edit = QtWidgets.QLineEdit()
        self.end_frame_edit.setText(str(hou.playbar.playbackRange()[1]))  # Set default to current end frame
        frame_layout.addWidget(QtWidgets.QLabel("End Frame:"))
        frame_layout.addWidget(self.end_frame_edit)

        self.layout.addLayout(frame_layout)

        # Horizontal layout for sequence and shot no inputs
        sequence_shot_layout = QtWidgets.QHBoxLayout()

        # Add empty Sequence No combo box
        self.sequence_no_combo = QtWidgets.QLineEdit()
        sequence_shot_layout.addWidget(QtWidgets.QLabel("Sequence No:"))
        sequence_shot_layout.addWidget(self.sequence_no_combo)

        # Add empty Shot No combo box
        self.shot_no_combo = QtWidgets.QLineEdit()
        sequence_shot_layout.addWidget(QtWidgets.QLabel("Shot No:"))
        sequence_shot_layout.addWidget(self.shot_no_combo)

        self.layout.addLayout(sequence_shot_layout)

        # Refresh button
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_nodes)
        self.layout.addWidget(self.refresh_button)
        self.refresh_button.setMinimumHeight(50)
        self.refresh_button.setStyleSheet("border-radius: 5px; font-weight: bold;")

        # File format header
        file_format_header = QtWidgets.QLabel("File Format")
        self.layout.addWidget(file_format_header)
        

        # File format buttons
        self.file_format_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.file_format_layout)

        self.ass_button = QtWidgets.QPushButton("ass")
        self.ass_button.setCheckable(True)
        self.ass_button.setChecked(True)  # Set "ass" button checked by default
        self.ass_button.clicked.connect(lambda: self.handle_file_format_button_click(self.ass_button))
        self.ass_button.setStyleSheet("background-color: #339933; border-radius: 5px;")  # Set background color to green for "ass" and rounded corners
        self.file_format_layout.addWidget(self.ass_button)
        self.ass_button.setMinimumHeight(30)

        self.abc_button = QtWidgets.QPushButton("abc")
        self.abc_button.setCheckable(True)
        self.abc_button.clicked.connect(lambda: self.handle_file_format_button_click(self.abc_button))
        self.file_format_layout.addWidget(self.abc_button)
        self.abc_button.setMinimumHeight(30)

        self.vdb_button = QtWidgets.QPushButton("vdb")
        self.vdb_button.setCheckable(True)
        self.vdb_button.clicked.connect(lambda: self.handle_file_format_button_click(self.vdb_button))
        self.file_format_layout.addWidget(self.vdb_button)
        self.vdb_button.setMinimumHeight(30)

        # Horizontal layout for version number
        version_layout = QtWidgets.QHBoxLayout()
        version_layout.setSpacing(0)
        version_layout.setContentsMargins(0, 0, 0, 0)
    
        # Text label to prompt user to select version
        self.select_version_label = QtWidgets.QLabel("Select Version:")
        self.select_version_label.setStyleSheet("font-weight: bold;")
        version_layout.addWidget(self.select_version_label)
    
        # Version number dropdown menu
        self.version_number_combo = QtWidgets.QComboBox()
        for i in range(1, 51):
            self.version_number_combo.addItem("{:03d}".format(i))
        version_layout.addWidget(self.version_number_combo)
        self.version_number_combo.setMinimumHeight(24)
        self.version_number_combo.setMinimumWidth(198)
        self.version_number_combo.setStyleSheet("background-color: #339933; border-radius: 5px; font-weight: bold;")
    
        self.layout.addLayout(version_layout)

        # Selected file format label
        self.selected_format_label = QtWidgets.QLabel("Selected Format: ass")  # Default to "ass"
        self.layout.addWidget(self.selected_format_label)
        
        self.export_path_checkbox = QtWidgets.QCheckBox("Export Path Attribute")
        self.export_path_checkbox.setChecked(False)
        self.layout.addWidget(self.export_path_checkbox)
        
        # Label to display selected node names
        self.selected_nodes_label = QtWidgets.QLabel("Selected Nodes:")
        self.layout.addWidget(self.selected_nodes_label)

        # Export and Cancel buttons in the same row
        buttons_layout = QtWidgets.QHBoxLayout()

        # Set the minimum width of the buttons
        button_height = 40

        self.export_button = QtWidgets.QPushButton("Export")
        self.export_button.setMinimumHeight(button_height)  # Set minimum width
        self.export_button.setMinimumWidth(220)
        self.export_button.clicked.connect(self.export_nodes)
        self.export_button.setStyleSheet("background-color: #339933; border-radius: 5px; font-weight: bold;")

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(button_height)  # Set minimum width
        self.cancel_button.setStyleSheet("background-color: #cf0000; border-radius: 5px; font-weight: bold;")

        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(buttons_layout)

        # Connect Cancel button
        self.cancel_button.clicked.connect(self.close)
        self.export_button.clicked.connect(self.close)

        self.refresh_nodes()
        self.select_all_nodes()
        # Initialize checkbox visibility based on initial button state
        self.toggle_export_path_checkbox()
        self.abc_button.clicked.connect(self.toggle_export_path_checkbox)
    
    def toggle_export_path_checkbox(self):
        # Show or hide the checkbox based on whether the "abc" button is checked
        if self.abc_button.isChecked():
            self.export_path_checkbox.setVisible(True)
        else:
            self.export_path_checkbox.setVisible(False)

    
    def refresh_nodes(self):
        self.nodes_list.clear()
        selected_nodes = hou.selectedNodes()
        for node in selected_nodes:
            item = QtWidgets.QListWidgetItem(node.name())
            self.nodes_list.addItem(item)

        # Update sequence and shot numbers based on hip file path
        seq_number, shot_number = self.extract_seq_shot_numbers()
        if seq_number is not None and shot_number is not None:
            self.sequence_no_combo.setText(seq_number)
            self.shot_no_combo.setText(shot_number)

        # Print sequence and shot numbers
        print("Sequence Number (q):", seq_number)
        print("Shot Number (s):", shot_number)

    def update_selected_nodes_label(self):
        selected_node_names = [item.text() for item in self.nodes_list.selectedItems()]
        self.selected_nodes_label.setText("Nodes: " + " ".join(selected_node_names))

    def handle_file_format_button_click(self, clicked_button):
        for button in [self.ass_button, self.abc_button, self.vdb_button]:
            if button != clicked_button:
                button.setChecked(False)
                button.setStyleSheet("")  # Reset style sheet for other buttons
            else:
                button.setStyleSheet("background-color: #339933; border-radius: 5px; font-weight: bold;")  # Set background color to green for the clicked button
        self.selected_format_label.setText("Selected Format: {}".format(clicked_button.text()))
        # Show or hide the checkbox based on the selected format
        if clicked_button == self.abc_button:
            self.export_path_checkbox.setVisible(True)
        else:
            self.export_path_checkbox.setVisible(False)

    def select_all_nodes(self):
        selected_nodes = hou.selectedNodes()

        # Select all nodes by default
        for i in range(self.nodes_list.count()):
            self.nodes_list.item(i).setSelected(True)

    def export_nodes(self):
        selected_items = self.nodes_list.selectedItems()
        if not selected_items:
            return  # No selected items to export

        selected_node_names = [item.text() for item in selected_items]

        # Get the start frame value from the QLineEdit widget
        start_frame = int(float(self.start_frame_edit.text()))
        end_frame = int(float(self.end_frame_edit.text()))

        # Get the hip file path and name
        hip_file_path = hou.hipFile.path()
        hip_file_name = hou.hipFile.basename()
        hou_name = hip_file_name[:19]

        # Get selected version number
        version_number = self.version_number_combo.currentText()
        version_name = "v{}".format(version_number)
        
        # Extract sequence and shot numbers
        seq_number = self.sequence_no_combo.text()
        shot_number = self.shot_no_combo.text()

        for node in hou.selectedNodes():
            if node.name() in selected_node_names:
                if self.selected_format_label.text().endswith('abc'):
                    # Create a geo node with the same name as the selected node + "_export"
                    geo_node = hou.node('/obj').createNode('geo', node.name() + '_export')

                    # Create an Object Merge node inside the Geo node
                    obj_merge_node = geo_node.createNode('object_merge')
                    obj_merge_node.parm('xformtype').set(1)  # Set xformtype parameter to 1

                    # Set objpath1 parameter to selected node's path
                    obj_merge_node.setParms({'objpath1': node.path()})

                    # Create an ROP Alembic node inside the Geo node
                    rop_alembic_node = geo_node.createNode('rop_alembic' ,node.name() + '_abc')

                    # Change the trange parameter to 2
                    rop_alembic_node.parm('trange').set(2)

                    # Delete the parameter values of t1 and t2
                    rop_alembic_node.parm('f1').deleteAllKeyframes()
                    rop_alembic_node.parm('f2').deleteAllKeyframes()

                    # Set parameter to the start frame and end frame
                    rop_alembic_node.parm('f1').set(start_frame)
                    rop_alembic_node.parm('f2').set(end_frame)

                    # Construct the file path
                    file_path = "$HIP/cache/abc/"+node.name()+"_C_001/"+version_name+"/st1_ft01_q"+seq_number+"_s"+shot_number+"_fx-fx_base-"+node.name()+"_C_001_"+version_name+".1000.abc"

                    # Set the filepath parameter
                    rop_alembic_node.parm('filename').set(file_path)
                    
                    # Set build_from_path based on checkbox state
                    build_from_path = 1 if self.export_path_checkbox.isChecked() else 0
                    rop_alembic_node.parm('build_from_path').set(build_from_path)
                    

                    # Connect Alembic node with Object Merge node
                    rop_alembic_node.setInput(0, obj_merge_node)

                    # Layout the nodes
                    geo_node.layoutChildren()

                    # Execute the ROP Alembic node
                    rop_alembic_node.parm('execute').pressButton()
                    geo_node.destroy()

                elif self.selected_format_label.text().endswith('vdb'):
                    #Create a geo node with the same name as the selected node + "_export"
                    geo_node = hou.node('/obj').createNode('geo', node.name() + '_export')

                    # Create an Object Merge node inside the Geo node
                    obj_merge_node = geo_node.createNode('object_merge')
                    obj_merge_node.parm('xformtype').set(1)  # Set xformtype parameter to 1

                    # Set objpath1 parameter to selected node's path
                    obj_merge_node.setParms({'objpath1': node.path()})

                    # Create a Convert VDB node
                    convert_vdb_node = geo_node.createNode('convertvdb')
                    convert_vdb_node.parm('conversion').set(1) 
                    convert_vdb_node.setInput(0, obj_merge_node)

                    # Create a File Cache node
                    file_cache_node = geo_node.createNode('filecache',node.name() + '_vdb')

                    # Change the trange parameter to 2
                    file_cache_node.parm('trange').set(2)
                    

                    # Delete the parameter values of t1 and t2
                    file_cache_node.parm('f1').deleteAllKeyframes()
                    file_cache_node.parm('f2').deleteAllKeyframes()

                    # Set parameter to the start frame and end frame
                    file_cache_node.parm('f1').set(start_frame)
                    file_cache_node.parm('f2').set(end_frame)

                    # Construct the file path
                    file_path = "$HIP/cache/vdb/"+node.name()+"_C_001/"+version_name+"/st1_ft01_q"+seq_number+"_s"+shot_number+"_fx-fx_base-"+node.name()+"_C_001_"+version_name+".$F4.vdb"

                    # Set the filepath parameter
                    file_cache_node.parm('file').set(file_path)

                    # Connect Alembic node with Object Merge node
                    file_cache_node.setInput(0, convert_vdb_node)

                    # Layout the nodes
                    geo_node.layoutChildren()

                    # Execute the ROP Alembic node
                    file_cache_node.parm('execute').pressButton()
                    geo_node.destroy()
                
                elif self.selected_format_label.text().endswith('ass'):

                    # Create a mantra node in the out level
                    out = hou.node('/out')
                    arnold_node = out.createNode('arnold', node.name() + '_ass')
                    
                    # Change the trange parameter to 2
                    arnold_node.parm('trange').set(2)
                    arnold_node.parm("vobject").set("")
                    arnold_node.parm("forceobject").set(node.name())
                    arnold_node.parm("ar_ass_export_enable").set(1)
                    arnold_node.parm("ar_ass_export_lights").set(0)
                    arnold_node.parm("ar_ass_export_cameras").set(0)
             
                    # Delete the parameter values of t1 and t2
                    arnold_node.parm('f1').deleteAllKeyframes()
                    arnold_node.parm('f2').deleteAllKeyframes()

                    # Set parameter to the start frame and end frame
                    arnold_node.parm('f1').set(start_frame)
                    arnold_node.parm('f2').set(end_frame)

                    # Construct the file path
                    file_path = "$HIP/cache/ass/"+node.name()+"_C_001/"+version_name+"/st1_ft01_q"+seq_number+"_s"+shot_number+"_fx-fx_base-"+node.name()+"_C_001_"+version_name+".$F4.ass"
                    # Set the filepath parameter
                    arnold_node.parm('ar_ass_file').set(file_path)

                    # Execute the ROP Alembic node
                    arnold_node.parm("execute").pressButton()
                    arnold_node.destroy()

    def extract_seq_shot_numbers(self):
        hip_file_path = hou.hipFile.path()
        seq_shot_match = re.search(r'/q(?P<seq>\d+)/s(?P<shot>\d+)', hip_file_path)
        if seq_shot_match:
            sequence = seq_shot_match.group('seq')
            shot = seq_shot_match.group('shot')
            return sequence, shot
        return None, None

# Create and show the UI
app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([])

ui = SelectedNodesUI()
ui.show()

