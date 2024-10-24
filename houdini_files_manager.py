import os
import re
import hou
import time
import getpass
import subprocess
import _alembic_hom_extensions as ahe
from collections import defaultdict
from PySide2 import QtGui, QtCore, QtWidgets

class SimpleUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SimpleUI, self).__init__(parent)
        
        # Set up the main layout
        self.setWindowTitle("HOU UI")
        self.setGeometry(750, 350, 548, 308)  # Increased width for Elements and Version
        self.hip_icon = QtGui.QIcon('/ASEX/share/sheetal.pathak/sheetal/Documents/STH/Script/icons/houdini.png')
        self.folder_icon = QtGui.QIcon('/ASEX/share/sheetal.pathak/sheetal/Documents/STH/Script/icons/folder.256x204.png')
        self.extra_icon = QtGui.QIcon('/ASEX/share/sheetal.pathak/sheetal/Documents/STH/Script/icons/document.png')
   
        # Initialize the folder path
        self.folder_path = '/srv/projects/st1/work/shots/ft01'
        
        # Create a main horizontal layout for the overall UI
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(0)  # Adjust spacing between items
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around the layout
        
        # Create a vertical layout for the input widgets
        self.input_layout = QtWidgets.QVBoxLayout()
        
        # Create a horizontal layout for Username
        self.username_layout = QtWidgets.QHBoxLayout()
        
        # Create and add the QLabel for Username
        self.username_label = QtWidgets.QLabel("Username:")
        self.username_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.username_layout.addWidget(self.username_label)
        
        # Create and add the QLineEdit for Username
        self.username_field = QtWidgets.QLineEdit()
        self.username_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.username_layout.addWidget(self.username_field)
        
        # Add the username layout to the input layout
        self.input_layout.addLayout(self.username_layout)
        
        # Create a horizontal layout for Sequence No and Shot No
        self.sequence_shot_layout = QtWidgets.QHBoxLayout()
        # Create and add the QLabel for Sequence No
        self.sequence_no_label = QtWidgets.QLabel("Sequence No:")
        self.sequence_no_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.sequence_shot_layout.addWidget(self.sequence_no_label)
        # Create and add the QComboBox for Sequence No
        self.sequence_no_combo = QtWidgets.QComboBox()
        self.sequence_no_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.sequence_shot_layout.addWidget(self.sequence_no_combo)
        # Create and add the QLabel for Shot No
        self.shot_no_label = QtWidgets.QLabel("Shot No:")
        self.shot_no_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.sequence_shot_layout.addWidget(self.shot_no_label)
        # Create and add the QComboBox for Shot No
        self.shot_no_combo = QtWidgets.QComboBox()
        self.shot_no_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.sequence_shot_layout.addWidget(self.shot_no_combo)
        # Create and add the Open Folder button
        self.open_folder_button = QtWidgets.QPushButton("GO TO Directory")
        self.open_folder_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.sequence_shot_layout.addWidget(self.open_folder_button)
        # Create and add the Refresh button
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.refresh_button.clicked.connect(self.refresh_all)
        self.sequence_shot_layout.addWidget(self.refresh_button)
        # Add the sequence and shot layout to the input layout
        self.input_layout.addLayout(self.sequence_shot_layout)
        
        # Create and add the QListWidget for Files
        self.files_list_widget = QtWidgets.QListWidget()
        self.files_list_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.files_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.input_layout.addWidget(self.files_list_widget)
        
        # Create a horizontal layout for Start, End, Elements, and Version
        self.playbar_elements_version_layout = QtWidgets.QHBoxLayout()
        # Create and add the QLabel for Start
        self.start_label = QtWidgets.QLabel("Start:")
        self.playbar_elements_version_layout.addWidget(self.start_label)
        # Create and add the QLineEdit for Start
        self.start_field = QtWidgets.QLineEdit()
        self.playbar_elements_version_layout.addWidget(self.start_field)
        # Create and add the QLabel for End
        self.end_label = QtWidgets.QLabel("End:")
        self.playbar_elements_version_layout.addWidget(self.end_label)
        # Create and add the QLineEdit for End
        self.end_field = QtWidgets.QLineEdit()
        self.playbar_elements_version_layout.addWidget(self.end_field)
        # Create and add the QLabel for Elements
        self.elements_label = QtWidgets.QLabel("Elements:")
        self.playbar_elements_version_layout.addWidget(self.elements_label)
        # Create and add the QLineEdit for Elements
        self.elements_field = QtWidgets.QLineEdit()
        self.elements_field.setReadOnly(False)  # Allow editing
        self.playbar_elements_version_layout.addWidget(self.elements_field)
        # Create and add the QLabel for Version
        self.version_label = QtWidgets.QLabel("Version:")
        self.playbar_elements_version_layout.addWidget(self.version_label)
        # Create and add the QComboBox for Version
        self.version_combo = QtWidgets.QComboBox()
        self.version_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        # Populate version dropdown with values from v001 to v100
        versions = ["v%03d" % i for i in range(1, 101)]
        self.version_combo.addItems(versions)
        # Add the version combo box to the layout
        self.playbar_elements_version_layout.addWidget(self.version_combo)
        # Add the playbar, elements, and version layout to the input layout
        self.input_layout.addLayout(self.playbar_elements_version_layout)
        
        # Create a horizontal layout for Save, Open, Import, and Build Scene buttons
        self.button_layout = QtWidgets.QHBoxLayout()
        # Create and add the Save button
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setStyleSheet("QPushButton { background-color: #222222; color: #FFFFFF; } QPushButton:hover { background-color: #666666; color: #000000; }")
        self.save_button.clicked.connect(self.save_file)
        self.button_layout.addWidget(self.save_button)
        # Create and add the Open button
        self.open_button = QtWidgets.QPushButton("Open")
        self.open_button.setStyleSheet("QPushButton { background-color: #222222; color: #FFFFFF; } QPushButton:hover { background-color: #666666; color: #000000; }")
        self.open_button.clicked.connect(self.open_file)
        self.button_layout.addWidget(self.open_button)
        # Create and add the Import button
        self.import_button = QtWidgets.QPushButton("Import")
        self.import_button.setStyleSheet("QPushButton { background-color: #222222; color: #FFFFFF; } QPushButton:hover { background-color: #666666; color: #000000; }")
        self.import_button.clicked.connect(self.import_file)
        self.button_layout.addWidget(self.import_button)
        # Create and add the Build Scene button
        self.build_scene_button = QtWidgets.QPushButton("Build Scene")
        self.build_scene_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.build_scene_button.clicked.connect(self.build_scene)
        self.button_layout.addWidget(self.build_scene_button)
        # Create and add the Update button
        self.update_button = QtWidgets.QPushButton("Update")
        self.update_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.update_button.clicked.connect(self.update_scene)
        self.button_layout.addWidget(self.update_button)
        # Add the button layout to the input layout
        self.input_layout.addLayout(self.button_layout)
        
        # Create a horizontal layout for Save, Open, Import, and Build Scene buttons
        self.flipbook_layout = QtWidgets.QHBoxLayout()
        # Create and add the Create Flipbook button
        self.build_scene_button = QtWidgets.QPushButton("Create Flipbook")
        self.build_scene_button.setStyleSheet("QPushButton { background-color: #339933; color: #FFFFFF; } QPushButton:hover { background-color: #00cc00; color: #000000; }")
        self.build_scene_button.setMinimumWidth(219.5)
        self.build_scene_button.clicked.connect(self.create_flipbook)
        self.flipbook_layout.addWidget(self.build_scene_button)
        # Create and add the Camera Clean button
        self.camera_clean_button = QtWidgets.QPushButton("Camera Clean")
        self.camera_clean_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.camera_clean_button.clicked.connect(self.clean_cameras)
        self.flipbook_layout.addWidget(self.camera_clean_button)
        # Create and add the Frustum button
        self.frustum_button = QtWidgets.QPushButton("Frustum")
        self.frustum_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.frustum_button.clicked.connect(self.create_frustum)
        self.flipbook_layout.addWidget(self.frustum_button)
        # Create and add the Set Renge button
        self.set_renge_button = QtWidgets.QPushButton("Set Renge")
        self.set_renge_button.setStyleSheet("QPushButton { background-color: #808080; color: #FFFFFF; } QPushButton:hover { background-color: #A9A9A9; color: #000000; }")
        self.set_renge_button.clicked.connect(self.set_range)
        self.flipbook_layout.addWidget(self.set_renge_button)
        # Add the button layout to the input layout
        self.input_layout.addLayout(self.flipbook_layout)
        
        # Add the input layout to the main layout
        self.main_layout.addLayout(self.input_layout)
        
        # Set the layout
        self.setLayout(self.main_layout)
        
        # Populate the QComboBox with sequence folders
        self.get_sequences(self.folder_path)
        
        # Connect the sequence combo box selection change event
        self.sequence_no_combo.currentIndexChanged.connect(self.update_sequence)
        self.shot_no_combo.currentIndexChanged.connect(self.update_file_list)
        
        # Set the username field with current username
        self.get_username()
        
        # Update the playbar values
        self.update_playbar_values()
        
        # Update the elements field with the current hip file's elements
        self.update_elements_field()
        
        # Set default sequence and shot based on hip file name
        self.set_default_sequence_shot()
        
        # Apply styles
        self.apply_styles()
    
    def apply_styles(self):
        # Set the dark theme for the entire widget
        dark_theme = """
        QWidget {
            background-color: #2E2E2E;
            color: #E0E0E0;
        }
        QLabel {
            color: #E0E0E0;
        }
        QLineEdit, QComboBox, QListWidget {
            background-color: #111111;
            color: #E0E0E0;
            border: 1px solid #4A4A4A;
            border-radius: 3px;
        }
        QPushButton {
            background-color: #000000;
            color: #E0E0E0;
            border: 1px solid #000000;
            border-radius: 3px;
            padding: 5px 5px;
            outline: none;
        }
        QPushButton:hover {
            background-color: #5A5A5A;
        }
        QPushButton:pressed {
            background-color: #6A6A6A;
        }
        QComboBox::drop-down {
            background-color: #111111;
            border: 1px solid #111111;
            border-radius: 3px;
        }
        
        """
        self.setStyleSheet(dark_theme)    
    
    def get_username(self):
        # Retrieve the current username
        username = os.getlogin()
        self.username_field.setText(username)
    
    def get_sequences(self, path):
        # Check if the path exists
        if not os.path.exists(path):
            QtWidgets.QMessageBox.warning(self, 'Error', 'Path does not exist!')
            return
        
        # List all folders in the path
        try:
            folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
            sorted_folders = sorted(folders)  # Sort the folder names alphabetically
            self.sequence_no_combo.addItems(sorted_folders)
            
            # Optionally, set the first item as selected to load shots
            if sorted_folders:
                self.sequence_no_combo.setCurrentIndex(0)
                self.update_sequence()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', str(e))
    
    def update_sequence(self):
        # Get the selected sequence folder
        selected_sequence = self.sequence_no_combo.currentText()
        if not selected_sequence:
            return
        
        # Construct the path for the selected sequence
        self.folder_path = os.path.join('/srv/projects/st1/work/shots/ft01', selected_sequence)
        
        # Populate the Shot No combo box
        self.get_shots(self.folder_path)
    
    def get_shots(self, path):
        # Clear existing items in the Shot No combo box
        self.shot_no_combo.clear()
        
        # Check if the path exists
        if not os.path.exists(path):
            return
        
        # List all folders in the path
        try:
            folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
            sorted_folders = sorted(folders)  # Sort the folder names alphabetically
            self.shot_no_combo.addItems(sorted_folders)
            
            # Optionally, set the first item as selected to load files
            if sorted_folders:
                self.shot_no_combo.setCurrentIndex(0)
                self.update_file_list()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', str(e))
    
    def update_file_list(self):
        # Get the selected shot folder
        selected_shot = self.shot_no_combo.currentText()
        if not selected_shot:
            return
        
        # Construct the path for the selected shot
        self.folder_path = os.path.join('/srv/projects/st1/work/shots/ft01',
                                        self.sequence_no_combo.currentText(),
                                        selected_shot, 'fx', 'fx', 
                                        self.username_field.text(), 'houdini')
        
        # Populate the file list widget
        self.refresh_file_list()
    
    def refresh_file_list(self):
        # Populate the file list widget
        self.list_files(self.folder_path)
    
    def list_files(self, path):
        # Clear existing items in the file list widget
        self.files_list_widget.clear()
        
        # Check if the path exists
        if not os.path.exists(path):
            return
        
        # List all files and folders in the path
        try:
            # Add a backslash item if not at root
            if path != '/srv/projects/st1/work/shots/ft01':
                backslash_item = QtWidgets.QListWidgetItem("\\")
                backslash_item.setForeground(QtGui.QColor('Khaki'))  # Red text for backslash
                self.files_list_widget.addItem(backslash_item)
            
            # Get all files and folders
            entries = [name for name in os.listdir(path) if os.path.exists(os.path.join(path, name))]
            entries.sort()  # Sort alphabetically
            
            # Add entries to the list widget
            for entry in entries:
                full_path = os.path.join(path, entry)
                item = QtWidgets.QListWidgetItem(entry)
                
                # Use different text colors for folders and files
                if os.path.isdir(full_path):
                    item.setForeground(QtGui.QColor('Khaki'))  # Blue text for folders
                    item.setIcon(self.folder_icon)
                elif entry.lower().endswith('.hip'):
                    item.setIcon(self.hip_icon)  # Set the .hip file icon
                    item.setForeground(QtGui.QColor('white'))  # Green text for files
                else:
                    item.setForeground(QtGui.QColor('white'))  # Green text for files
                    item.setIcon(self.extra_icon)
                
                self.files_list_widget.addItem(item)
        
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', str(e))
    
    def on_item_double_clicked(self, item):
        item_name = item.text()
        
        # Handle the backslash navigation
        if item_name == "\\":
            self.on_backslash_clicked()
            return
        
        new_path = os.path.join(self.folder_path, item_name)
        
        if os.path.isdir(new_path):
            self.folder_path = new_path
            self.refresh_file_list()
    
    def on_backslash_clicked(self):
        # Navigate one step back in the folder path
        self.folder_path = os.path.dirname(self.folder_path)
        self.refresh_file_list()
    
    def update_playbar_values(self):
        # Get the Houdini playbar start and end values
        try:
            start_frame = hou.playbar.frameRange()[0]
            end_frame = hou.playbar.frameRange()[1]
            self.start_field.setText(str(int(start_frame)))
            self.end_field.setText(str(int(end_frame)))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Could not retrieve playbar values: %s' % str(e))

    def update_elements_field(self):
        # Extract the elements from the current Houdini hip file path
        try:
            hip_file_path = hou.hipFile.path()
            if not hip_file_path:
                self.elements_field.setText("No file loaded")
                return
            
            # Extract the part of the filename after "fx-fx_" and before "_v"
            base_name = os.path.basename(hip_file_path)
            if "fx-fx_" in base_name and "_v" in base_name:
                elements = base_name.split("fx-fx_")[1].split("_v")[0]
            else:
                elements = "Unknown"
            self.elements_field.setText(elements)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Could not retrieve elements: %s' % str(e))
    
    def set_default_sequence_shot(self):
        # Get the name of the current Houdini hip file
        current_hip_file = hou.hipFile.path()
        if not current_hip_file:
            print("No hip file loaded")
            return
        
        print("Current hip file path: %s" % current_hip_file)
        
        # Extract version from the file name
        version_match = re.search(r'_v(\d{3})', current_hip_file)
        if version_match:
            version = "v%03d" % int(version_match.group(1))
            print("Extracted version: %s" % version)
            index = self.version_combo.findText(version)
            if index >= 0:
                self.version_combo.setCurrentIndex(index)
            else:
                print("Version %s not found in combo box" % version)
        
        # Extract sequence number from the file name
        sequence_match = re.search(r'q(\d+)', current_hip_file)
        if sequence_match:
            sequence_no = sequence_match.group(1)
            print("Extracted sequence number: %s" % sequence_no)
            seq_index = self.sequence_no_combo.findText('q' + sequence_no)
            if seq_index >= 0:
                self.sequence_no_combo.setCurrentIndex(seq_index)
                self.update_sequence()  # Update the shot numbers
            else:
                print("Sequence number %s not found in combo box" % sequence_no)
        
        # Extract shot number from the file name
        shot_match = re.search(r's(\d+)', current_hip_file)
        if shot_match:
            shot_no = shot_match.group(1)
            print("Extracted shot number: %s" % shot_no)
            shot_index = self.shot_no_combo.findText('s' + shot_no)
            if shot_index >= 0:
                self.shot_no_combo.setCurrentIndex(shot_index)
            else:
                print("Shot number %s not found in combo box" % shot_no)
    
    def save_file(self):
        # Get the current sequence, shot, elements, and version
        sequence_no = self.sequence_no_combo.currentText()
        shot_no = self.shot_no_combo.currentText()
        elements = self.elements_field.text()
        version = self.version_combo.currentText()
        
        # Construct the filename
        if not sequence_no or not shot_no:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Sequence No or Shot No is not selected!')
            return
        
        # Using % formatting for Python 2.7
        hip_file_name = "st1_ft01_%s_%s_fx-fx_%s_%s.hip" % (sequence_no, shot_no, elements, version)
        
        # Get the path to save the file
        save_path = os.path.join(self.folder_path, hip_file_name)
        
        # Ensure the directory exists
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Error', 'Could not create directory: %s' % str(e))
                return
        
        # Save the Houdini file
        try:
            hou.hipFile.save(save_path)
            QtWidgets.QMessageBox.information(self, 'Success', 'File saved as %s' % hip_file_name)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Could not save file: %s' % str(e))
        self.refresh_all()

        
    def open_file(self):
        # Get the selected file from the file list widget
        selected_item = self.files_list_widget.currentItem()
        if not selected_item:
            QtWidgets.QMessageBox.warning(self, 'Error', 'No file selected!')
            return
        
        file_name = selected_item.text()
        if file_name == "\\":
            QtWidgets.QMessageBox.warning(self, 'Error', 'Cannot open a folder!')
            return
        
        # Construct the full path of the selected file
        file_path = os.path.join(self.folder_path, file_name)
        
        # Open the Houdini file
        try:
            hou.hipFile.load(file_path)
            QtWidgets.QMessageBox.information(self, 'Success', 'File opened: %s' % file_name)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Could not open file: %s' % str(e))
        self.refresh_all()
    
    def import_file(self):
        # Get the selected file from the file list widget
        selected_item = self.files_list_widget.currentItem()
        if not selected_item:
            QtWidgets.QMessageBox.warning(self, 'Error', 'No file selected!')
            return
        
        file_name = selected_item.text()
        if file_name == "\\":
            QtWidgets.QMessageBox.warning(self, 'Error', 'Cannot import a folder!')
            return
        
        # Construct the full path of the selected file
        file_path = os.path.join(self.folder_path, file_name)
        base_name = os.path.splitext(file_name)[0]
        # Create an Alembic Archive node and set its filePath parameter
        try:
            # Create a new Alembic Archive node
            alembic_node = hou.node('/obj').createNode('alembicarchive')
            alembic_node.setName(base_name, unique_name=True)
            
            # Set the filePath parameter of the Alembic Archive node
            alembic_node.parm('fileName').set(file_path)
            alembic_node.parm("buildSingleGeoNode").set(1)
            alembic_node.parm("buildHierarchy").pressButton()

            QtWidgets.QMessageBox.information(self, 'Success', 'Alembic Archive node created and file path set.')
        
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Could not import Alembic file: %s' % str(e))
    
    def build_scene(self):
        # Get the sequence and shot numbers from the input fields
        Sequence_No = self.sequence_no_combo.currentText()
        Shot_No = self.shot_no_combo.currentText()
        
        # Construct the directory path
        directory_path = "/srv/projects/st1/library/shots/ft01/{}/{}/tch/techAnim/abc/".format(Sequence_No, Shot_No)
    
        # Check if the directory exists
        if not os.path.exists(directory_path):
            hou.ui.displayMessage("Directory not found: {}".format(directory_path))
            return
    
        # Initialize a dictionary to store the latest version of each Alembic file
        latest_alembic_files = defaultdict(lambda: ["", 0])
    
        # Traverse through the directory and its subdirectories
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".abc"):
                    file_path = os.path.join(root, file)
                    file_name, version = self.extract_file_info(file)
                    if version > latest_alembic_files[file_name][1]:
                        latest_alembic_files[file_name] = [file_path, version]
    
        # Check if any Alembic file is found
        if not latest_alembic_files:
            hou.ui.displayMessage("No Alembic files found in directory: {}".format(directory_path))
            return
    
        # Create a null node to merge all Alembic nodes
        obj_network = hou.node("/obj")
        merge_null = obj_network.createNode("null", node_name="Merged_Alembics")
    
        # Create an empty list to store Alembic nodes
        alembic_nodes = []
    
        # Create an AlembicArchive node for each latest version Alembic file
        for file_name, (file_path, version) in latest_alembic_files.items():
            # Create an AlembicArchive node
            alembic_node = obj_network.createNode("alembicarchive", node_name=file_name)
            # Set the Alembic file path
            alembic_node.parm("fileName").set(file_path)
            alembic_node.parm("buildSingleGeoNode").set(1)
            alembic_node.parm("buildHierarchy").pressButton()
            # Add the Alembic node to the list
            alembic_nodes.append(alembic_node)
    
        # Merge all Alembic nodes under the null node
        for node in alembic_nodes:
            node.setNextInput(merge_null)
    
        # Layout the nodes in the scene
        obj_network.layoutChildren()
    
        # Get the camera path
        camera_path = "/srv/projects/st1/library/shots/ft01/{}/{}/tch/techAnim/abc/caCraneCam01_C_001/".format(Sequence_No, Shot_No)
    
        # Check if the camera file directory exists
        if not os.path.exists(camera_path):
            hou.ui.displayMessage("Camera file directory not found: {}".format(camera_path))
            return
    
        # List files in the camera directory to find the latest version
        camera_files = os.listdir(camera_path)
    
        if not camera_files:
            hou.ui.displayMessage("No camera files found in directory: {}".format(camera_path))
            return
    
        # Sort the files by modification time to get the latest version
        latest_camera_file = max(camera_files, key=lambda f: os.path.getmtime(os.path.join(camera_path, f)))
    
        # Get the full path of the latest camera file
        camera_file_path = os.path.join(camera_path, latest_camera_file)
    
        # Check if the file exists
        if not os.path.exists(camera_file_path):
            hou.ui.displayMessage("Camera file not found: {}".format(camera_file_path))
            return

   
        # Get the time range from the imported Alembic file
        start_time, end_time = ahe.alembicTimeRange(camera_file_path)
        start = int(start_time * 24)
        end = int(end_time * 24)
        print(start)


        # Set the frame range in the Houdini playbar
        hou.playbar.setFrameRange(start, end)
        hou.playbar.setPlaybackRange(hou.playbar.playbackRange()[0], end)
    
        # Save the scene
        self.save_file()
        
    def extract_file_info(self, file_name):
        # Example extraction logic, modify as needed based on your file naming convention
        # Assuming file_name format is: filename_vX.abc where X is the version number
        name_parts = file_name.split("_v")
        if len(name_parts) != 2:
            return "", 0
        file_name = name_parts[0]
        version = int(name_parts[1].split(".")[0])
        return file_name, version

        print("Set Scene button clicked.")    
    
    def update_scene(self):
        # Get the selected Alembic nodes
        selected_nodes = hou.selectedNodes()
        if not selected_nodes:
            hou.ui.displayMessage("Please select Alembic nodes to update.")
            return
    
        for node in selected_nodes:
            # Check if the selected node is an Alembic node
            if node.type().name() == "alembicarchive":
                # Get the current fileName parameter value of the selected node
                current_file_path = node.parm("fileName").eval()
    
                # Extract the base path (directory) and file name from the current file path
                base_path, file_name = os.path.split(current_file_path)
    
                # Extract the base name without the version number
                base_name, file_ext = os.path.splitext(file_name)
                base_name_parts = base_name.split("_v")
                base_name_without_version = base_name_parts[0] if len(base_name_parts) > 0 else base_name
    
                # Initialize variables to store the latest version and file path
                latest_version = -1
                latest_file_path = None
    
                # Search for files with the same base name in the base path directory
                for file in os.listdir(base_path):
                    if file.startswith(base_name_without_version) and file.endswith(".abc"):
                        # Extract the version number from the file name
                        version_str = file.split("_v")[-1].split(".")[0]
                        try:
                            version = int(version_str)
                        except ValueError:
                            continue  # Skip files with invalid version format
    
                        # Update latest version and file path if a higher version is found
                        if version > latest_version:
                            latest_version = version
                            latest_file_path = os.path.join(base_path, file)
    
                # Check if a higher version is found
                if latest_version > -1:
                    # Update the fileName parameter of the selected node with the latest version file path
                    node.parm("fileName").set(latest_file_path)
                    node.setColor(hou.Color((0, 1, 0)))  # Set node label color to green
                    hou.ui.setStatusMessage("Updated {} to a higher version: {}".format(node.name(), latest_version))
                else:
                    hou.ui.displayMessage("No higher version found for {}.".format(node.name()))
            else:
                hou.ui.displayMessage("Node {} is not an Alembic node.".format(node.name()))    
    
    def create_flipbook(self):
        cur_desktop = hou.ui.curDesktop()
        scene_viewer = hou.paneTabType.SceneViewer
        scene = cur_desktop.paneTabOfType(scene_viewer)
        scene.flipbookSettings().stash()
        flip_book_options = scene.flipbookSettings()

        # Retrieve start and end frames from the text fields
        start_text = self.start_field.text()
        end_text = self.end_field.text()
    
        # Convert text to integer, defaulting to None if invalid
        start_frame = int(start_text) if start_text.isdigit() else None
        end_frame = int(end_text) if end_text.isdigit() else None
    
        # Check if the start and end frames are valid
        if start_frame is None or end_frame is None:
            hou.ui.displayMessage("Invalid frame range. Please check the start and end frame values.")
            return
        
        # Set the flipbook frame range
        flip_book_options.frameRange((start_frame, end_frame))
        version_value = self.version_combo.currentText()

        flipbook_folder = os.path.join(self.folder_path, "flipbooks", version_value)  # Add leading zeros
        if not os.path.exists(flipbook_folder):
            os.makedirs(flipbook_folder)

        hip_file_name = os.path.basename(hou.hipFile.name())
        flipbook_filename = hip_file_name.split(".")[0] + ".$F4.jpeg"
        flipbook_output_path = os.path.join(flipbook_folder, flipbook_filename)

        flip_book_options.output(flipbook_output_path)  # Provide flipbook full path with padding.
        flip_book_options.useResolution(1)
        flip_book_options.resolution((2072, 1120))  # Based on your camera resolution

        scene.flipbook(scene.curViewport(), flip_book_options)
        hou.ui.setStatusMessage("Generating Flipbook...")

        # Wait for flipbook generation to complete
        while True:
            flipbook_files = [f for f in os.listdir(flipbook_folder) if f.endswith('.jpeg')]
            if len(flipbook_files) >= (end_frame - start_frame + 1):  # Corrected frame range condition
                break
            time.sleep(1)

        # Debug: print flipbook files
        print("Flipbook files:", flipbook_files)

        # Get the latest audio file based on q_value and s_value
        audio_folder = "/srv/projects/st1/library/shots/ft01/{}/{}/snd/sound/wav".format(self.sequence_no_combo.currentText(), self.shot_no_combo.currentText())
        latest_audio_file = self.get_latest_audio_file(audio_folder)
        # Print the path of the latest audio file
        print("Latest audio file path:", latest_audio_file)

        # Convert JPEG sequence to video using FFmpeg
        self.convert_jpeg_sequence_to_video(flipbook_folder, latest_audio_file)

    def get_latest_audio_file(self, audio_folder):
        # Get all WAV files in the specified folder
        audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.wav')]
        if not audio_files:
            print("No WAV files found in:", audio_folder)
            return None

        # Find the latest modified audio file
        latest_audio_file = max(audio_files, key=lambda f: os.path.getmtime(os.path.join(audio_folder, f)))
        return os.path.join(audio_folder, latest_audio_file)

    def convert_jpeg_sequence_to_video(self, jpeg_folder, audio_file):
        hip_file_path = hou.hipFile.path()
        hip_file_name = hou.hipFile.basename()
        name = hip_file_name[:-4]
        start_text = self.start_field.text()
        start_frame = int(start_text) if start_text.isdigit() else None
    
        output_file = os.path.join(os.path.dirname(hip_file_path), "flipbooks", name + ".mov")
        # Check if the output_file exists and remove it if necessary
        if os.path.exists(output_file):
            os.remove(output_file)
    
        start = start_frame  # Adjust the start frame number if necessary
        framerate = 24
        offset_value =2500
    
        # Add date overlay to video using drawtext filter
        
        date_overlay = "drawtext=text='%{localtime\\:%Y-%m-%d}': fontsize=10: fontcolor=white: x=8: y=8"
        username_overlay = ", drawtext=text='{username}': fontsize=10: fontcolor=white: x=8: y=16".format(username=self.username_field.text())
        frame_overlay = ", drawtext=text='Current Frame: %{expr\\:n+" + str(start) + "}': fontsize=10: fontcolor=white: x=(w-text_w+36): y=(h-text_h-8)"
  
        ffmpeg_command = [
            '/srv/projects/st1/pipeline/toolsExternal/staticbuilds/lx64/ffmpeg-git-20171110-64bit-static/ffmpeg',  # Full path to ffmpeg executable
            '-start_number', str(start),  # Specify the start frame number
            '-framerate', str(framerate),
            '-i', '{}/{}.%4d.jpeg'.format(jpeg_folder, name),
            '-i', audio_file,  # Input audio file
            '-vf', date_overlay + username_overlay + frame_overlay,
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'pcm_s16le',  # Audio codec (PCM 16-bit signed little-endian)
            '-strict', 'experimental',
            '-b:a', '192k',  # Audio bitrate
            '-shortest',  # Finish encoding when the shortest input stream ends
            output_file
        ]
    
        # Print the ffmpeg command
        print("FFmpeg Command:", ' '.join(ffmpeg_command))
    
        try:
            subprocess.call(ffmpeg_command)
            print('Successfully created {}'.format(output_file))
        except subprocess.CalledProcessError as e:
            print('Error: {}'.format(e))
    
        hou.ui.setStatusMessage("Flipbook MP4 Done...")
    
    def clean_cameras(self):
        # Define the clean_cameras method logic here
        def find_node_by_name(node_name):
            # Iterate through all nodes in the scene
            for node in hou.node('/').allSubChildren():
                # Check if the node's name matches the target name
                if node.name() == node_name:
                    return node
            return None

        # Name of the node to search for
        node_names = ["stereoCam_C_001_STCM", "mirrorFeature_C_001_GRUP"]

        # Find and delete the nodes
        for node_name in node_names:
            node = find_node_by_name(node_name)
            if node:
                # Delete the node
                node.destroy()
                print("Node '{}' deleted.".format(node_name))
            else:
                print("Node '{}' not found.".format(node_name))        
    
    def create_frustum(self):
        # Function to find the camera node
        def find_camera_node(node):
            # Check if the current node is a camera node
            if node.type().name() == 'cam':
                return node
            else:
                # If not, recursively search through its children
                for child in node.children():
                    result = find_camera_node(child)
                    if result:
                        return result
                # If no camera node is found in the subtree, return None
                return None

        # Start the search from the root node
        root_node = hou.node('/')
        cam_node = find_camera_node(root_node)
        if cam_node:
            hou.ui.displayMessage("Camera node found: {}".format(cam_node.path()))
            # Execute the code if camera node is found
            # Create a new geometry node
            geo_node = hou.node("/obj").createNode('geo', node_name='frustum')
            
            # Create a box node inside the geometry node
            box_node = geo_node.createNode("box")
            
            # Set the center of the box
            center = hou.Vector3(0.5, 0.5, -0.5)
            box_node.parmTuple("t").set(center)
            
            # Create a Wrangle node after the box
            wrangle_node = geo_node.createNode("attribwrangle", node_name='depth')
            
            # Add a depth parameter to the Wrangle node
            depth_parm = wrangle_node.addSpareParmTuple(hou.FloatParmTemplate("depth", "Depth", 1, default_value=(100,), min=0))
            
            # Connect the box node to the input of the Wrangle node
            wrangle_node.setInput(0, box_node)
            
            # Write the code snippet in the Wrangle node
            wrangle_node.parm("snippet").set("if(@P.z < 0){ @P.z += -chf('depth'); }")
            
            # Create a Divide node after the Wrangle node
            divide_node = geo_node.createNode("divide")
            divide_node.parm("usemaxsides").set(0)
            divide_node.parm("brick").set(1)
            
            # Connect the Wrangle node to the input of the Divide node
            divide_node.setInput(0, wrangle_node)
            
            # Set the size parameters of the Divide node
            divide_node.parm("sizex").setExpression("ch('../depth/depth') / 2.8")
            divide_node.parm("sizey").setExpression("ch('../depth/depth') / 2.8")
            divide_node.parm("sizez").setExpression("ch('../depth/depth') / 2.8")
            
            # Create a new Wrangle node after the Divide node
            wrangle_node_2 = geo_node.createNode("attribwrangle", node_name='Opacity')
            
            # Connect the Divide node to the input of the second Wrangle node
            wrangle_node_2.setInput(0, divide_node)
            
            # Write the code snippet in the second Wrangle node
            wrangle_node_2.parm("snippet").set("@Alpha*=chf('opacity');\nf@col=fit(@P.z,0,chf('depth'),0,1);")
            
            # Add the Alpha parameter to the second Wrangle node
            alpha_param = wrangle_node_2.addSpareParmTuple(hou.FloatParmTemplate("opacity", "Alpha", 1, default_value=(0.5,), min=0, max=1))
            
            # Add the Depth parameter to the second Wrangle node
            depth_param = wrangle_node_2.addSpareParmTuple(hou.FloatParmTemplate("depth", "Depth", 1, default_value=(-100,), min=-1000, max=0))
            
            # Set the expression for the Depth parameter
            depth_param[0].setExpression("-ch('../depth/depth')")
            wrangle_node_2.parm("class").set("primitive")
            
            color_node = geo_node.createNode("color")
            # Set parameters for the Color SOP node
            color_node.parm('class').set(1)
            color_node.parm('colortype').set(3)
            color_node.parm('rampattribute').set("col") 
            color_node.parm('ramp1cr').set(1)
            color_node.parm('ramp2cb').set(0)
            color_node.parm('ramp2cr').set(0)
            color_node.setInput(0, wrangle_node_2)
            
            # Create an Attribute VOP node after the second Wrangle node
            attribute_vop_node = geo_node.createNode("attribvop",)
            attribute_vop_node .setInput(0, color_node)
     
            # Create a "From NDC" VOP node inside the Attribute VOP node
            from_ndc_node = attribute_vop_node.createNode('fromndcgeo')
            geometryvopglobal_node = attribute_vop_node.createNode('geometryvopglobal')
            geometryvopoutput_node = attribute_vop_node.createNode('geometryvopoutput')
            
            from_ndc_node.setInput(0, geometryvopglobal_node,0)
            geometryvopoutput_node.setInput(0, from_ndc_node,0)
 
            #set flag and layout for the nodes
            attribute_vop_node.setDisplayFlag(True)
            attribute_vop_node.setRenderFlag(True)
            geo_node.layoutChildren()
    
        if cam_node:
            #frustum_node.parm('Camera_Select').set(cam_node.path())
            from_ndc_node.parm("camera").set(cam_node.path())
       
        else:
            hou.ui.displayMessage("No camera node found in the scene.")
    
    def set_range(self):
        # Get the sequence and shot numbers from the input fields
        sequence_no = self.sequence_no_combo.currentText()
        shot_no = self.shot_no_combo.currentText()

        # Construct the camera directory path
        camera_path = "/srv/projects/st1/library/shots/ft01/{}/{}/tch/techAnim/abc/caCraneCam01_C_001/".format(sequence_no, shot_no)

        # Check if the camera directory exists
        if not os.path.exists(camera_path):
            hou.ui.displayMessage("Camera file directory not found: {}".format(camera_path))
            return

        # List files in the camera directory to find the latest version
        camera_files = os.listdir(camera_path)

        if not camera_files:
            hou.ui.displayMessage("No camera files found in directory: {}".format(camera_path))
            return

        # Sort the files by modification time to get the latest version
        latest_camera_file = max(camera_files, key=lambda f: os.path.getmtime(os.path.join(camera_path, f)))

        # Get the full path of the latest camera file
        camera_file_path = os.path.join(camera_path, latest_camera_file)

        # Check if the file exists
        if not os.path.exists(camera_file_path):
            hou.ui.displayMessage("Camera file not found: {}".format(camera_file_path))
            return

        # Get the time range from the imported Alembic file
        start_time, end_time = ahe.alembicTimeRange(camera_file_path)
        start_frame = int(start_time * 24)
        end_frame = int(end_time * 24)
        # Set the frame range in the Houdini playbar
        hou.playbar.setFrameRange(start_frame, end_frame)
        hou.playbar.setPlaybackRange(hou.playbar.playbackRange()[0], end_frame)

        # Update the start and end frame text boxes in the UI
        self.entry_start.setText(str(start_frame))
        self.entry_end.setText(str(end_frame))

        hou.ui.setStatusMessage("Frame range set from camera file.")       

    def refresh_all(self):
        # Refresh all fields
        self.get_username()
        self.update_playbar_values()
        self.update_elements_field()
        self.set_default_sequence_shot()
    
    def open_folder(self):
        # Open the folder path in Caja file browser
        if os.path.exists(self.folder_path):
            try:
                subprocess.Popen(['caja', self.folder_path])
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Error', str(e))
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Folder path does not exist!')

def show_ui():
    # Make sure the UI is not already open
    if hasattr(hou.ui, 'simple_ui') and hou.ui.simple_ui.isVisible():
        hou.ui.simple_ui.raise_()
        return
    
    # Create the UI instance and show it
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    ui = SimpleUI()
    ui.show()
    
    # Keep a reference to the UI to prevent garbage collection
    hou.ui.simple_ui = ui

# Execute the UI function
show_ui()

