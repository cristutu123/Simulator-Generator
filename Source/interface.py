import os
import tkinter as tk
import customtkinter as ctk
import files
from objects import Argument, TestStep, TestCase, cmd, Filter
from tkinter import messagebox, Text, simpledialog, ttk
from pathlib import Path
import json

# Set CustomTkinter appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# THIS FUNCTION WILL BE CALLED WHEN THE APP STARTS
def show_debug_message():
	import tkinter.messagebox as mb
	mb.showinfo("Debug Info", "The correct interface.py file is being used!")

COLOR_BLACK = ''

class App:
	def __init__(self, root):
		# Remove debug message call
		# show_debug_message()
		
		# 
		self.root = root
		self.root.title("Test Step Generator")
		self.root.state("zoomed")  # Set the application to full screen
		self.root.configure(bg="#1e1e1e")  # Darker background color for the root

		# Set frame layout
		self.root.grid_columnconfigure(1, weight=1)
		self.root.grid_rowconfigure(0, weight=1)

		# Sidebar on the left with CustomTkinter
		self.sidebar_width = int(self.root.winfo_screenwidth() * 0.14)
		self.sidebar_frame = ctk.CTkFrame(root, width=self.sidebar_width, corner_radius=0)
		self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
		self.sidebar_frame.grid_rowconfigure(1, weight=1)  # For file list to expand

		# App title in sidebar
		self.app_title = ctk.CTkLabel(
			self.sidebar_frame, 
			text="Test Step Generator", 
			font=ctk.CTkFont(size=20, weight="bold"),
			pady=15
		)
		self.app_title.grid(row=0, column=0, padx=20, pady=(20, 10))

		# File list frame with scrollable area
		self.file_list_container = ctk.CTkFrame(self.sidebar_frame, corner_radius=0)
		self.file_list_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
		self.file_list_container.grid_rowconfigure(0, weight=1)
		self.file_list_container.grid_columnconfigure(0, weight=1)

		# Scrollable frame for file list
		self.file_list_scrollable = ctk.CTkScrollableFrame(self.file_list_container)
		self.file_list_scrollable.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
		self.file_list_scrollable.grid_columnconfigure(0, weight=1)

		# File list frame (will contain file buttons)
		self.file_list_frame = self.file_list_scrollable
		
		# Button container for add/remove file buttons
		self.file_actions_frame = ctk.CTkFrame(self.sidebar_frame)
		self.file_actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
		self.file_actions_frame.grid_columnconfigure(0, weight=1)
		self.file_actions_frame.grid_columnconfigure(1, weight=1)

		# Add file button
		self.add_file_btn = ctk.CTkButton(
			self.file_actions_frame, 
			text="Add File", 
			command=self.add_test_case,
			fg_color="green",
			hover_color="#006400"
		)
		self.add_file_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

		# Remove file button
		self.remove_file_btn = ctk.CTkButton(
			self.file_actions_frame, 
			text="Remove File",
			command=self.remove_test_case,
			fg_color="#AA5555",
			hover_color="#993333"
		)
		self.remove_file_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

		# Main content frame
		self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
		self.main_frame.grid(row=0, column=1, sticky="nsew")
		self.main_frame.grid_rowconfigure(1, weight=1)  # Test steps row - less weight
		self.main_frame.grid_rowconfigure(2, weight=3)  # Preview row - more weight
		self.main_frame.grid_columnconfigure(0, weight=1)

		# Header for current file title
		self.file_title_label = ctk.CTkLabel(
			self.main_frame, 
			text="Please select a file", 
			font=ctk.CTkFont(size=24, weight="bold"),
			anchor="w"
		)
		self.file_title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

		# Test steps container
		self.test_steps_container = ctk.CTkFrame(self.main_frame)
		self.test_steps_container.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
		self.test_steps_container.grid_columnconfigure(0, weight=1)
		self.test_steps_container.grid_rowconfigure(1, weight=1)

		# Test steps label
		self.test_steps_label = ctk.CTkLabel(
			self.test_steps_container,
			text="Test Steps",
			font=ctk.CTkFont(size=16, weight="bold"),
			anchor="w"
		)
		self.test_steps_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

		# Scrollable frame for test steps
		self.test_step_scrollable = ctk.CTkScrollableFrame(
			self.test_steps_container,
			orientation="horizontal",
			height=80  # Reduced height
		)
		self.test_step_scrollable.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
		
		# Test step frame (will contain step buttons)
		self.test_step_frame = self.test_step_scrollable

		# Preview container
		self.preview_container = ctk.CTkFrame(self.main_frame)
		self.preview_container.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
		self.preview_container.grid_columnconfigure(0, weight=1)
		self.preview_container.grid_rowconfigure(1, weight=1)

		# Preview label
		self.preview_label = ctk.CTkLabel(
			self.preview_container,
			text="Preview",
			font=ctk.CTkFont(size=16, weight="bold"),
			anchor="w"
		)
		self.preview_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

		# Preview text widget
		self.preview_text = ctk.CTkTextbox(
			self.preview_container,
			font=ctk.CTkFont(family="Courier New", size=16),  # Increased font size
			wrap="word"
		)
		self.preview_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
		self.preview_text.insert("1.0", "Select a file and test step to view preview")
		self.preview_text.configure(state="disabled")

		# Control bar
		self.control_frame = ctk.CTkFrame(self.main_frame)
		self.control_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

		# Control buttons
		self.add_step_btn = ctk.CTkButton(
			self.control_frame, 
			text="ADD", 
			command=lambda: self.add_test_step(self.current_test_case),
			width=100
		)
		self.add_step_btn.pack(side="left", padx=5, pady=10)

		self.edit_step_btn = ctk.CTkButton(
			self.control_frame,
			text="EDIT",
			command=self.edit_test_step,
			width=100
		)
		self.edit_step_btn.pack(side="left", padx=5, pady=10)

		self.remove_step_btn = ctk.CTkButton(
			self.control_frame,
			text="REMOVE",
			command=self.remove_test_step,
			width=100
		)
		self.remove_step_btn.pack(side="left", padx=5, pady=10)

		self.help_btn = ctk.CTkButton(
			self.control_frame,
			text="HELP",
			command=self.view_help_files,
			width=100
		)
		self.help_btn.pack(side="left", padx=5, pady=10)
		
		# Generate button
		self.generate_button = ctk.CTkButton(
			self.control_frame,
			text="Generate File",
			command=self.generate_file,
			width=150,
			fg_color="#228B22",  # Forest green
			hover_color="#006400"  # Dark green
		)
		self.generate_button.pack(side="right", padx=5, pady=10)

		self.test_case_label = ""
		self.current_test_case = None  # Track selected file
		self.selected_test_step_index = None  # Track selected test step index
		self.test_steps = {}
		self.test_cases = {}  # In-memory storage for test steps
		self.load_test_cases()
		#self.load_commands()  # Load commands from JSON

	def get_command_category(self, command_name):
		"""Determine the category of a command based on its name"""
		if command_name.startswith("[PRECHECK]"):
			return "Precheck"
		elif command_name.startswith("[PRECOND]"):
			return "Precondition"
		elif command_name.startswith("[CROSS]"):
			return "Cross"
		elif command_name.startswith("[RUN]"):
			return "Run"
		else:
			return "Other"
			
	def load_commands(self):
		try:
			with open('../Models/dlhif.json', 'r') as f:
				self.commands_data = json.load(f)
		except Exception as e:
			print(f"Error loading dlhif.json: {e}")
			self.commands_data = {}

	# Method to load commands from all files containing 'help.txt' in their name
	def load_commands_from_file(self):
		commands = []
		# Define the directory path
		directory_path = os.path.join("../../../Test/Simulation/Input")
		
		# Find all files containing 'help.txt' in their name
		for filename in os.listdir(directory_path):
			if "help.txt" in filename.lower():
				file_path = os.path.join(directory_path, filename)
				with open(file_path, "r") as f:
					content = f.read()
					# Split each block 
					blocks = content.split("============================================================================================")
					for block in blocks:
						block = block.strip()
						if not block:  # Skip empty block
							continue
						try:
							# Parse each section of the block
							lines = block.split("\n")
							name_line = [line for line in lines if line.startswith("Name:")][0]
							description_line = [line for line in lines if line.startswith("Description:")][0]
							arguments_line = [line for line in lines if line.startswith("Arguments:")][0]
							default_line = [line for line in lines if line.startswith("Default:")][0]

							name = name_line.split(":", 1)[1].strip()
							description = description_line.split(":", 1)[1].strip()
							arguments_raw = arguments_line.split(":", 1)[1].strip()
							default = default_line.split(":", 1)[1].strip()

							arguments = []
							if arguments_raw != "None":
								for arg in arguments_raw.split():
									arguments.append(Argument(name=arg, description="", arg_type="string", default=""))

							commands.append(cmd(name=name, description=description, arguments=arguments, default=default))
						except Exception as e:
							print(f"Error parsing block: {block}\n{e}")
		return commands

	def load_test_cases(self):
		for widget in self.file_list_frame.winfo_children():
			widget.destroy()
		  
		self.file_buttons = []

		self.test_cases = files.get_test_cases()
		
		if not self.test_cases:
			no_files_label = ctk.CTkLabel(
				self.file_list_frame, 
				text="No files found",
				font=ctk.CTkFont(size=14)
			)
			no_files_label.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
		else:
			for i, test_case in enumerate(self.test_cases):
				self.test_steps[test_case.name] = test_case.test_steps
				
				# Create a modern button for each file
				btn = ctk.CTkButton(
					self.file_list_frame, 
					text=test_case.name,
					font=ctk.CTkFont(size=14),
					command=lambda tc=test_case.name: self.select_test_case(tc),
					height=50,
					fg_color="transparent",
					text_color=("gray10", "gray90"),
					hover_color=("gray70", "gray30"),
					anchor="center"
				)
				btn.grid(row=i, column=0, padx=5, pady=3, sticky="ew")
				self.file_buttons.append(btn)

		# Always show the "Create New File" button as the last item in the list
		create_file_button = ctk.CTkButton(
			self.file_list_frame, text="+", command=self.add_test_case,
			fg_color="green", 
			text_color=("gray90", "gray90"), 
			font=ctk.CTkFont(size=12, weight="bold"), width=int(self.sidebar_width * 0.135), height=2
		)
		create_file_button.grid(row=len(self.test_cases), column=0, padx=5, pady=2, sticky="ew")

		# Add Remove File button
		remove_file_button = ctk.CTkButton(
			self.file_list_frame, text="-", command=self.remove_test_case,
			fg_color="#994444", 
			text_color=("gray90", "gray90"), 
			font=ctk.CTkFont(size=12, weight="bold"), width=int(self.sidebar_width * 0.135), height=2
		)
		remove_file_button.grid(row=len(self.test_cases) + 1, column=0, padx=5, pady=10, sticky="ew")

	def add_test_case(self):
		file_name = simpledialog.askstring("Create New File", "Enter the name of the new file (without extension):")
		if file_name:
			files.create_test_case(file_name)
			self.load_test_cases()

	def remove_test_case(self):
		if self.current_test_case:
			answer = messagebox.askyesno("Remove File", f"Are you sure you want to delete '{self.current_test_case}'?")
			if answer:
				files.delete_test_case(self.current_test_case) 
				self.current_test_case = None
				self.clear_test_steps()  # Clear test steps when file is removed
				self.load_test_cases()
		else:
			messagebox.showwarning("Remove File", "No file selected for removal.")


	def select_test_case(self, test_case_name):
		self.current_test_case = test_case_name
		self.test_case_label = test_case_name  # Update the header with the file name
		self.file_title_label.configure(text=f"Selected File: {test_case_name}")  # Update the file title label
		self.selected_test_step_index = None  # Reset any selected test step

		# Reset all buttons to default styling
		for btn in self.file_buttons:
			if isinstance(btn, ctk.CTkButton):
				btn.configure(fg_color="transparent", border_width=0)
			else:
				btn.configure(relief="raised", bg="#3d3d3d")

		# Highlight the selected button
		for btn in self.file_buttons:
			if btn.cget("text") == test_case_name:
				if isinstance(btn, ctk.CTkButton):
					btn.configure(fg_color=("gray70", "gray30"), border_width=2)
				else:
					btn.configure(relief="solid", borderwidth=2, bg="#555555")

		self.load_test_steps(test_case_name)


	def clear_test_steps(self):
		for widget in self.test_step_frame.winfo_children():
			widget.destroy()
		self.preview_text.configure(state="normal")
		self.preview_text.delete("1.0", "end")
		self.preview_text.insert("1.0", "Please select a file")
		self.preview_text.tag_configure("center", justify="center")
		self.preview_text.tag_add("center", "1.0", "end")
		self.preview_text.configure(state="disabled")


	def load_test_steps(self, test_case_name):
		test_steps = []

		for widget in self.test_step_frame.winfo_children():
			widget.destroy()

		for test_case in self.test_cases:
			if test_case.name == test_case_name:
				test_steps = test_case.test_steps
				break

		for step in test_steps:
			step_index = step.index  # Store step index in a local variable to avoid closure issues
			step_button = ctk.CTkButton(
				self.test_step_frame, 
				text=f"Test Step {step_index + 1}", 
				fg_color="#505050",
				text_color=("gray90", "gray90"), 
				width=150, 
				height=40,
				command=lambda i=step_index: self.select_test_step(i)
			)
			step_button.bind("<Double-1>", lambda event, idx=step_index: self.edit_step_with_index(idx))
			step_button.pack(side="left", padx=5, pady=2)

	def select_test_step(self, index):
		self.selected_test_step_index = index
		
		# Print debug info to ensure we're setting the correct index
		print(f"Selected test step index: {self.selected_test_step_index}")
		
		# Reset all buttons to default styling
		for widget in self.test_step_frame.winfo_children():
			if isinstance(widget, ctk.CTkButton):
				widget.configure(fg_color="#505050", border_width=0)
			else:
				widget.configure(relief="flat", bg="#505050")
			
		# Find the selected button and highlight it
		for i, button in enumerate(self.test_step_frame.winfo_children()):
			if i == index:
				if isinstance(button, ctk.CTkButton):
					button.configure(fg_color="#777777", border_width=2)
				else:
					button.configure(relief="solid", borderwidth=2, bg="#777777")
				break
		
		# Update the preview with the selected test step data
		self.update_preview(self.test_steps[self.current_test_case][int(index)])

	

	def update_preview(self, content):
		newline = "\n"
		text = (
			"=================================================================================\n"
			f"Test step {content.index + 1} : {content.title}\n"
			"-------------------------------------------------------------------------------\n"
			f"Requirements: {content.requirements}\n"
			"-------------------------------------------------------------------------------\n"
			f"Description : {newline.join(f'{line}' for line in content.description)}\n"
			"-------------------------------------------------------------------------------\n"
			f"Expected    : {newline.join(f'{line}' for line in content.expected)}\n"
			"=================================================================================\n"
		)
		# Add commands to the display
		for cmd in content.inputs:
			text += f"{cmd['name']} {cmd['default']}\n"
		text += '\n'



		self.preview_text.configure(state="normal")
		self.preview_text.delete("1.0", "end")
		self.preview_text.insert("1.0", text)
		self.preview_text.configure(state="disabled")

	def view_selected_test_step(self):
		if self.selected_test_step_index is not None:
			test_case = self.current_test_case
			step_data = self.test_steps[test_case][self.selected_test_step_index]
			self.view_test_step(step_data)
		else:
			messagebox.showwarning("Select Test Step", "Please select a test step to view.")

	def add_test_step(self, test_case):
		self.open_test_step_editor(test_case, None, None)

	def edit_test_step(self):
		if self.selected_test_step_index is not None:
			test_case = self.current_test_case
			step_data = self.test_steps[test_case][int(self.selected_test_step_index)]
			self.open_test_step_editor(test_case, step_data, int(self.selected_test_step_index))
		else:
			messagebox.showwarning("Select Test Step", "Please select a test step to edit.")

	def open_test_step_editor(self, test_case, step_data, step_index):
		add_popup = ctk.CTkToplevel(self.root)
		add_popup.title("Edit Test Step" if step_data else "Add Test Step")
		add_popup.geometry("1100x850")  # Increased from 900x700 for better visibility
		add_popup.grab_set()  # Make the window modal

		# Create a notebook for tabbed interface
		notebook = ttk.Notebook(add_popup)
		notebook.pack(fill="both", expand=True, padx=10, pady=10)
		
		# Style the notebook tabs with a completely new approach
		style = ttk.Style()
		# Create new style with explicit color settings
		try:
			# First try to use the theme if it exists
			style.theme_use("CustomDark")
		except tk.TclError:
			# If it doesn't exist, create it
			style.theme_create("CustomDark", parent="alt", settings={
				"TNotebook": {"configure": {"background": "#2b2b2b", "borderwidth": 0}},
				"TNotebook.Tab": {"configure": {"background": "#3b3b3b", "padding": [10, 5], 
											  "font": ("Arial", 10)},
								"map": {"background": [("selected", "#1f6aa5"), ("!selected", "#3b3b3b")],
										"foreground": [("selected", "white"), ("!selected", "black")]}}
			})
		style.theme_use("CustomDark")
		
		# Tab 1: Basic Information
		basic_tab = ctk.CTkFrame(notebook)
		notebook.add(basic_tab, text="Basic Information")
		
		# Tab 2: Commands
		commands_tab = ctk.CTkFrame(notebook)
		notebook.add(commands_tab, text="Commands")
		
		# Fields for basic test step details
		fields = {
			"title": "Title of Test Step:",
			"requirements": "Requirements:",
			"description": "Description of Setup:",
			"expected": "Expected Results:"
		}
		contents = {
			"title": step_data.title if step_data else "",
			"requirements": step_data.requirements if step_data else "",
			"description": step_data.description[0] if step_data and step_data.description else "",
			"expected": step_data.expected[0] if step_data and step_data.expected else "",
		}
		entries = {}
		text_widgets = {}

		# Live preview update function
		def update_live_preview():
			# Get text from multi-line text widgets
			description_text = text_widgets["description"].get("1.0", "end-1c") if "description" in text_widgets else ""
			expected_text = text_widgets["expected"].get("1.0", "end-1c") if "expected" in text_widgets else ""
			
			# Gather selected commands from the command list
			selected_commands = []
			for cmd_instance in command_instances:
				if cmd_instance["active"].get():
					cmd_name = cmd_instance["name"]
					cmd_default = cmd_instance["entry"].get() if cmd_instance["entry"] else ""
					selected_commands.append({"name": cmd_name, "default": cmd_default})

			# Check if test_case is None
			if test_case is None:
				messagebox.showwarning("No Test Case", "Please select a test case first.")
				return

			# Construct a TestStep object with current field values and commands
			step_preview = TestStep(
				index=step_index if step_data else len(self.test_steps[test_case]),
				title=entries["title"].get() if "title" in entries and hasattr(entries["title"], "get") else "",
				requirements=entries["requirements"].get() if "requirements" in entries and hasattr(entries["requirements"], "get") else "",
				description=[description_text],
				expected=[expected_text],
				inputs=selected_commands
			)
			local_update_preview(step_preview)

		# Create main content frame in basic tab
		content_frame = ctk.CTkFrame(basic_tab)
		content_frame.pack(fill="both", expand=True, padx=20, pady=20)
		
		# Configure grid columns
		content_frame.columnconfigure(0, weight=0, minsize=150)  # Fixed width for labels
		content_frame.columnconfigure(1, weight=1)  # Expandable width for inputs
		
		# Create fields using grid layout
		row = 0
		for key, label_text in fields.items():
			# Create label
			label = ctk.CTkLabel(
				content_frame, 
				text=label_text, 
				font=ctk.CTkFont(size=14, weight="bold"),
				anchor="e",
			)
			label.grid(row=row, column=0, sticky="e", padx=(10, 15), pady=15)
			
			# Create different input widgets based on field type
			if key in ["description", "expected"]:
				# Use TextBox widget for multi-line input
				text_widget = ctk.CTkTextbox(
					content_frame, 
					height=100 if key == "description" else 100,
					font=ctk.CTkFont(size=12),
					wrap="word"
				)
				text_widget.insert("1.0", contents[key])
				text_widget.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=15)
				text_widget.bind("<KeyRelease>", lambda e: update_live_preview())
				text_widgets[key] = text_widget
				
				# Create a StringVar that will be updated with the Text widget content
				string_var = tk.StringVar(value=contents[key])
				entries[key] = string_var
			else:
				# Use Entry widget for single-line input
				entry = ctk.CTkEntry(
					content_frame, 
					font=ctk.CTkFont(size=12),
					height=35
				)
				entry.insert(0, contents[key])
				entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=15)
				entry.bind("<KeyRelease>", lambda e: update_live_preview())
				entries[key] = entry
			
			row += 1
		
		# Add preview area in basic tab
		preview_frame = ctk.CTkFrame(basic_tab)
		preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
		
		preview_label = ctk.CTkLabel(
			preview_frame, 
			text="Preview:", 
			font=ctk.CTkFont(size=14, weight="bold"),
			anchor="w"
		)
		preview_label.pack(anchor="w", pady=(15, 5))
		
		preview_text = ctk.CTkTextbox(
			preview_frame, 
			font=ctk.CTkFont(family="Courier New", size=12),
			height=150,
			wrap="word"
		)
		preview_text.pack(fill="both", expand=True)
		
		# Override update_live_preview to update the preview text
		original_update_preview = self.update_preview
		def local_update_preview(content):
			try:
				# Format the preview text
				newline = "\n"
				text = (
					f"Test step {content.index + 1} : {content.title}\n"
					f"Requirements: {content.requirements}\n"
					f"Description : {newline.join(f'{line}' for line in content.description)}\n"
					f"Expected    : {newline.join(f'{line}' for line in content.expected)}\n"
					f"Commands    : {len(content.inputs)} selected\n"
				)
				
				# Check if preview_text still exists before updating
				if preview_text.winfo_exists():
					preview_text.delete("1.0", "end")
					preview_text.insert("1.0", text)
				
				# Also update the main preview
				original_update_preview(content)
			except Exception as e:
				# If there's an error (likely because widget was destroyed), just update main preview
				print(f"Preview update error (non-critical): {e}")
				original_update_preview(content)
			
		self.update_preview = local_update_preview
		
		# Commands tab content
		commands_content = ctk.CTkFrame(commands_tab)
		commands_content.pack(fill="both", expand=True, padx=20, pady=20)
		
		# Top section: Filter controls
		filter_frame = ctk.CTkFrame(commands_content)
		filter_frame.pack(fill="x", pady=(0, 15))
		
		# Category filter
		category_label = ctk.CTkLabel(
			filter_frame,
			text="Category:",
			font=ctk.CTkFont(size=12),
			anchor="w"
		)
		category_label.pack(side="left", padx=(0, 5))
		
		# Replace ttk.Combobox with CTkOptionMenu
		self.category_filter_var = tk.StringVar(value="All")
		self.category_filter = ctk.CTkOptionMenu(
			filter_frame,
			values=["All", "Precheck", "Precondition", "Cross", "Run"],
			variable=self.category_filter_var,
			width=120,
			dynamic_resizing=False
		)
		self.category_filter.pack(side="left")
		
		# Search field
		search_label = ctk.CTkLabel(
			filter_frame,
			text="Search:",
			font=ctk.CTkFont(size=12),
			anchor="w"
		)
		search_label.pack(side="left", padx=(20, 5))
		
		self.search_var = tk.StringVar()
		search_entry = ctk.CTkEntry(
			filter_frame,
			textvariable=self.search_var,
			width=250,
			placeholder_text="Search commands..."
		)
		search_entry.pack(side="left", padx=5)
		
		# Command lists frame - completely restructure this with explicit heights
		lists_frame = ctk.CTkFrame(commands_content)
		lists_frame.pack(fill="both", expand=True, pady=10)
		lists_frame.columnconfigure(0, weight=1)
		lists_frame.columnconfigure(1, weight=0)
		lists_frame.columnconfigure(2, weight=1)
		# Force specific heights
		lists_frame.rowconfigure(0, weight=0, minsize=30)  # Header row
		lists_frame.rowconfigure(1, weight=1, minsize=300)  # Force this row to be drastically taller (from 500 to 700)
		
		# Configure row weight to allow expansion
		lists_frame.rowconfigure(1, weight=1)

		# Available commands section
		avail_label = ctk.CTkLabel(
			lists_frame,
			text="Available Commands:",
			font=ctk.CTkFont(size=14, weight="bold"),
			anchor="w"
		)
		avail_label.grid(row=0, column=0, sticky="w", padx=10, pady=(0, 5))
		
		# Selected commands section with remove all button
		selected_header = ctk.CTkFrame(lists_frame)
		selected_header.grid(row=0, column=2, sticky="ew", padx=10, pady=(0, 5))
		selected_header.columnconfigure(0, weight=1)
		selected_header.columnconfigure(1, weight=0)
		
		selected_label = ctk.CTkLabel(
			selected_header,
			text="Selected Commands:",
			font=ctk.CTkFont(size=14, weight="bold"),
			anchor="w"
		)
		selected_label.grid(row=0, column=0, sticky="w")
		
		remove_all_btn = ctk.CTkButton(
			selected_header,
			text="Remove All",
			command=lambda: remove_all_commands(),
			fg_color="#994444",
			hover_color="#773333",
			width=100
		)
		remove_all_btn.grid(row=0, column=1, sticky="e")
		
		# Command listbox (available commands)
		command_list_frame = ctk.CTkScrollableFrame(lists_frame, height=400)  # Reduced height from 700 to 400
		command_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
		command_list_frame.grid_rowconfigure(0, weight=1)
		command_list_frame.grid_columnconfigure(0, weight=1)

		# Listbox for available commands with matching font size to right side
		command_listbox = tk.Listbox(
			command_list_frame, 
			bg="#2b2b2b",  # Darker background for better contrast
			fg="#DCE4EE",  # Light text for visibility
			selectbackground="#1f6aa5",
			selectforeground="white",
			font=("Arial", 13),  # Adjusted font size to match the right side
			borderwidth=0,
			highlightthickness=1,
			highlightbackground="#555555",
			height=20  # Reduced height from 40 to 30
		)
		command_listbox.pack(fill="both", expand=True)  # Ensure both fill and expand are set to True
		
		# Middle buttons
		buttons_frame = ctk.CTkFrame(lists_frame)
		buttons_frame.grid(row=1, column=1, padx=10)

		add_cmd_button = ctk.CTkButton(
			buttons_frame, 
			text="Add →",
			command=lambda: add_command_to_list(),
			width=100
		)
		add_cmd_button.pack(pady=10)

		# Selected commands frame
		selected_list_frame = ctk.CTkScrollableFrame(lists_frame, height=400)  # Added explicit height of 400
		selected_list_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=5)
		
		# Configure column weights for selected_list_frame to ensure proper element sizing
		selected_list_frame.columnconfigure(0, weight=1)  # Make inner frames fill width

		# Description display - move up in the UI order and increase visibility
		desc_frame = ctk.CTkFrame(commands_content)
		desc_frame.pack(fill="x", pady=(10, 0))
		
		desc_label = ctk.CTkLabel(
			desc_frame,
			text="Description:",
			font=ctk.CTkFont(size=14, weight="bold"),  # Increased font size
			anchor="w"
		)
		desc_label.pack(anchor="w", padx=10, pady=(5, 0))
		
		description_text = ctk.CTkTextbox(
			desc_frame,
			height=80,  # Increased height from 60 to 80
			wrap="word",
			font=ctk.CTkFont(size=13)  # Increased font size
		)
		description_text.pack(fill="x", padx=10, pady=5)

		# Load commands and populate the available commands listbox
		all_commands = self.load_commands_from_file()
		command_dict = {}  # Store commands by name for easy lookup
		command_instances = []  # List to store all command instances
		
		# Populate the available commands listbox
		for cmd_obj in all_commands:
			command_listbox.insert(tk.END, f"{cmd_obj.name} - {cmd_obj.description}")
			command_dict[cmd_obj.name] = cmd_obj
			
		# Update description when selection changes
		def on_select(event):
			selection = command_listbox.curselection()
			if selection:
				selected_text = command_listbox.get(selection[0])
			cmd_name = selected_text.split(" - ")[0]
			if cmd_name in command_dict:
					cmd_obj = command_dict[cmd_name]
					description_text.delete("1.0", "end")
					description_text.insert("1.0", cmd_obj.description)
		
		command_listbox.bind("<<ListboxSelect>>", on_select)
		
		# Function to remove all commands
		def remove_all_commands():
			if command_instances:
				if messagebox.askyesno("Remove All", "Are you sure you want to remove all commands?"):
					for cmd_instance in command_instances[:]:  # Create a copy of the list to iterate
						cmd_instance["frame"].destroy()
					command_instances.clear()
					update_live_preview()
				
		# Function to add a command instance to the UI
		def add_command_instance(cmd_obj, default_value=""):
			try:
				# Create a frame for this command instance with padding
				cmd_frame = ctk.CTkFrame(selected_list_frame)
				cmd_frame.pack(fill="x", padx=5, pady=5, anchor="w")
				
				# Use grid instead of pack for better control of layout
				cmd_frame.columnconfigure(0, weight=0, minsize=250)  # Reduced width for checkbox
				cmd_frame.columnconfigure(1, weight=1)  # Make entry expandable
				cmd_frame.columnconfigure(2, weight=0, minsize=30)   # Small fixed width for remove button
			
				# Checkbox to enable/disable this command
				active_var = tk.BooleanVar(value=True)
				checkbox = ctk.CTkCheckBox(
					cmd_frame, 
					text=cmd_obj.name,
					variable=active_var,
					command=update_live_preview,
					font=ctk.CTkFont(size=13),  # Adjusted font size to match left side
					width=250  # Reduced width to allow more space for entry
				)
				checkbox.grid(row=0, column=0, padx=5, sticky="w")
				
				# Entry for arguments if any - expanded
				entry_widget = None
				if cmd_obj.arguments and cmd_obj.arguments[0].name != "None":
					entry_widget = ctk.CTkEntry(
						cmd_frame, 
						width=300,  # Increased width
						height=25
					)
					entry_widget.insert(0, default_value or cmd_obj.default)
					entry_widget.grid(row=0, column=1, padx=5, sticky="ew")
					entry_widget.bind("<KeyRelease>", lambda e: update_live_preview())
			
				# Keep remove button the same
				remove_btn = ctk.CTkButton(
					cmd_frame, 
					text="✕",
					font=ctk.CTkFont(size=14, weight="bold"),
					fg_color="#FF0000",  # Bright red for visibility
					hover_color="#CC0000",
					width=30,  # Compact width
					height=30,  # Same height
					corner_radius=5,  # Smaller corner radius for a box look
					command=lambda: remove_command_instance(cmd_instance_data)
				)
				# Use sticky="e" to keep it right-aligned and always visible
				remove_btn.grid(row=0, column=2, padx=(5, 5), sticky="e")
			
				# Store the command instance data
				cmd_instance_data = {
					"frame": cmd_frame,
					"active": active_var,
					"name": cmd_obj.name,
					"entry": entry_widget,
					"arguments": cmd_obj.arguments
				}
				command_instances.append(cmd_instance_data)
				
				# Update the live preview to include this command
				update_live_preview()
			
				return cmd_instance_data
			except Exception as e:
				messagebox.showerror("Error", f"Failed to add command: {str(e)}")
				print(f"Error adding command: {e}")
				return None
			
		# Function to remove a command instance
		def remove_command_instance(cmd_instance):
			cmd_instance["frame"].destroy()
			command_instances.remove(cmd_instance)
			update_live_preview()
		
		# Add existing commands to the selected list
		if step_data and step_data.inputs:
			for cmd_input in step_data.inputs:
				cmd_name = cmd_input["name"]
				cmd_default = cmd_input["default"]
				if cmd_name in command_dict:
					add_command_instance(command_dict[cmd_name], cmd_default)
					
		# Function to add a command to the selected list
		def add_command_to_list():
			selection = command_listbox.curselection()
			if not selection:
				messagebox.showinfo("Select Command", "Please select a command from the available list")
				return
			
			# Check if a test case is selected
			if test_case is None:
				messagebox.showwarning("No Test Case", "Please select a test case first.")
				return
				
			selected_index = selection[0]
			selected_text = command_listbox.get(selected_index)
			cmd_name = selected_text.split(" - ")[0]
			
			if cmd_name in command_dict:
				add_command_instance(command_dict[cmd_name])
				# Keep focus on listbox and maintain selection
				command_listbox.focus_set()
				if selected_index < command_listbox.size():
					command_listbox.selection_set(selected_index)
					command_listbox.see(selected_index)
				
		# Double-click to add command
		command_listbox.bind("<Double-Button-1>", lambda e: add_command_to_list())
		
		# Enter key to add command
		def on_enter(event):
			if event.widget == command_listbox:
				add_command_to_list()
				
		command_listbox.bind("<Return>", on_enter)
		
		# Function to filter commands based on category and search text
		def filter_commands(*args):
			search_text = self.search_var.get().lower()
			category = self.category_filter_var.get()
			
			# Clear the listbox
			command_listbox.delete(0, tk.END)
			
			# Filter and add matching commands
			for cmd_obj in all_commands:
				cmd_category = self.get_command_category(cmd_obj.name)
				cmd_name = cmd_obj.name.lower()
				cmd_desc = cmd_obj.description.lower()
				
				# Check category match
				category_match = category == "All" or cmd_category == category
				
				# Check search match
				search_match = True
				if search_text:
					search_match = search_text in cmd_name or search_text in cmd_desc
				
				# Add command to listbox if it matches both filters
				if category_match and search_match:
					command_listbox.insert(tk.END, f"{cmd_obj.name} - {cmd_obj.description}")
		
		# Bind filter events
		self.category_filter_var.trace_add("write", filter_commands)
		self.search_var.trace_add("write", filter_commands)

		# Save button logic
		def save_test_step():
			try:
				# Get text from multi-line text widgets
				description_text = text_widgets["description"].get("1.0", "end-1c")
				expected_text = text_widgets["expected"].get("1.0", "end-1c")
				
				# Gather selected commands from the command instances
				selected_commands = []
				for cmd_instance in command_instances:
					if cmd_instance["active"].get():
						cmd_name = cmd_instance["name"]
						cmd_default = cmd_instance["entry"].get() if cmd_instance["entry"] else ""
						selected_commands.append({"name": cmd_name, "default": cmd_default})

				# Determine index for the test step
				if step_data:
					# For editing, preserve the original index
					new_index = step_data.index
				else:
					# For adding, use the next available index
					new_index = len(self.test_steps[test_case])

				# Create or update the test step
				step = TestStep(
					index=new_index,
					title=entries["title"].get(),
					requirements=entries["requirements"].get(),
					description=[description_text],
					expected=[expected_text],
					inputs=selected_commands
				)

				# Update the test steps list
				if step_index is not None:
					# This is an edit
					self.test_steps[test_case][step_index] = step
				else:
					# This is an add
					self.test_steps[test_case].append(step)

				# Update the UI and close the popup
				self.update_preview(step)
				add_popup.destroy()
				self.load_test_steps(test_case)
				
				# Select the test step that was just added/edited
				self.select_test_step(step.index)
				messagebox.showinfo("Success", "Test step saved successfully!")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to save test step: {str(e)}")
				print(f"Error in save_test_step: {e}")

		# Create a more prominent save button
		save_button = ctk.CTkButton(
			add_popup, 
			text="Save Test Step", 
			command=save_test_step, 
			fg_color="#2E8B57",  # Sea Green
			hover_color="#1D6E41",  # Darker green
			font=ctk.CTkFont(size=16, weight="bold"),  # Increased font size
			height=50,  # Increased height from 40 to 50
			width=200  # Added explicit width
		)
		save_button.pack(pady=20)  # Increased padding

	def view_help_files(self):
		"""Display help files in a popup window"""
		help_popup = tk.Toplevel(self.root)
		help_popup.title("Command Help Files")
		help_popup.geometry("900x700")
		help_popup.configure(bg="#333333")
		
		# Create a frame for the help content
		help_frame = tk.Frame(help_popup, bg="#333333")
		help_frame.pack(fill="both", expand=True, padx=10, pady=10)
		
		# Create a notebook for tabbed viewing of help files
		notebook = ttk.Notebook(help_frame)
		notebook.pack(fill="both", expand=True)
		
		# Find all help files
		directory_path = os.path.join("../../../Test/Simulation/Input")
		help_files = []
		
		for filename in os.listdir(directory_path):
			if "help.txt" in filename.lower():
				help_files.append((filename, os.path.join(directory_path, filename)))
		
		# Create a tab for each help file
		for filename, filepath in help_files:
			tab = tk.Frame(notebook, bg="#444444")
			notebook.add(tab, text=filename)
			
			# Add scrollable text widget to display file content
			text_frame = tk.Frame(tab, bg="#444444")
			text_frame.pack(fill="both", expand=True, padx=5, pady=5)
			
			scrollbar = tk.Scrollbar(text_frame)
			scrollbar.pack(side="right", fill="y")
			
			help_text = tk.Text(text_frame, bg="#444444", fg="white", wrap="word", font=("Courier New", 12))
			help_text.pack(side="left", fill="both", expand=True)
			
			scrollbar.configure(command=help_text.yview)
			help_text.configure(yscrollcommand=scrollbar.set)
			
			# Load and display file content
			try:
				with open(filepath, 'r') as f:
					content = f.read()
					help_text.insert("1.0", content)
					help_text.configure(state="disabled")  # Make read-only
			except Exception as e:
				help_text.insert("1.0", f"Error loading file: {e}")
				help_text.configure(state="disabled")
		
		# If no help files found
		if not help_files:
			tab = tk.Frame(notebook, bg="#444444")
			notebook.add(tab, text="No Help Files")
			
			no_files_label = tk.Label(
				tab, 
				text="No help files found in the input directory.", 
				bg="#444444", 
				fg="white",
				font=("Arial", 14)
			)
			no_files_label.pack(pady=50)
			
	def generate_file(self):
		if not self.current_test_case:
			messagebox.showwarning("No File Selected", "Please select a file to generate.")
			return

		# Path to save the file
		file_path = os.path.join("../../../Test/Simulation/Input", f"{self.current_test_case}.in")

		try:
			with open(file_path, 'w') as file:
				for step in self.test_steps[self.current_test_case]:
					# Write the test step in the proper format
					newline = "\n"
					file.write(
						"=================================================================================\n"
						f"Test step {step.index + 1} : {step.title}\n"
						"-------------------------------------------------------------------------------\n"
						f"Requirements: {step.requirements}\n"
						"-------------------------------------------------------------------------------\n"
						f"Description : {newline.join(f'{line}' for line in step.description)}\n"
						"-------------------------------------------------------------------------------\n"
						f"Expected    : {newline.join(f'{line}' for line in step.expected)}\n"
						"=================================================================================\n"
					)
					for cmd in step.inputs:
						file.write(f"{cmd['name']} {cmd['default']}\n")
					file.write('\n')
				  

			messagebox.showinfo("File Generated", f"The file '{self.current_test_case}.in' has been successfully generated.")
		except Exception as e:
			messagebox.showerror("Error", f"An error occurred while generating the file: {e}")

	def remove_test_step(self):
		if self.selected_test_step_index is not None:
			if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this test step?"):
				test_case = self.current_test_case
				del self.test_steps[test_case][int(self.selected_test_step_index)]  # Delete from memory

				self.selected_test_step_index = None
				self.load_test_steps(test_case)
				self.update_preview("")  # Clear preview
			else:
				messagebox.showwarning("Select Test Step", "Please select a test step to remove.")
		else:
			messagebox.showwarning("Select Test Step", "Please select a test step to remove.")

	def edit_step_with_index(self, index):
		"""Helper function to handle double-click event on test step buttons"""
		self.select_test_step(index)
		self.edit_test_step()
