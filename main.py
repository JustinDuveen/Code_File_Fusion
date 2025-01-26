import streamlit as st
import os
import base64
import re
import pandas as pd

# Define directories, file extensions, and patterns to exclude
EXCLUDE_DIRS = ['.git', 'venv', '__pycache__', 'node_modules', 'dist', 'build', 'models', 'embeddings', 'checkpoints']
EXCLUDE_EXTENSIONS = ['.pyc', '.log', '.tmp', '.cache', '.pkl', '.DS_Store', '.onnx', '.bin', '.pt', '.h5']
EXCLUDE_PATTERNS = [r'bert', r'all-mini-lm', r'\.onnx$', r'\.bin$', r'\.pt$', r'\.h5$']
SENSITIVE_FILES = ['.env', 'secrets.json', 'config.yml']  # Add other sensitive files here

def is_binary(file_path):
    """Check if a file is binary by reading a small chunk and checking for non-text characters."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk  # Binary files often contain null bytes
    except Exception:
        return True  # Assume binary if there's an error reading the file

def should_exclude_file(file_name):
    """Check if a file should be excluded based on its name or pattern."""
    # Check for sensitive files
    if file_name in SENSITIVE_FILES:
        return True
    
    # Check for excluded extensions
    if any(file_name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
        return True
    
    # Check for excluded patterns using regex
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_name, re.IGNORECASE):
            return True
    
    return False

def read_file_contents(file_path):
    """Read the contents of a file, handling both text and binary files."""
    try:
        if is_binary(file_path):
            with open(file_path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8'), True  # Encode binary as Base64
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read(), False
    except Exception as e:
        return f"Error reading file: {e}", False

def generate_structure_diagram(root_dir):
    """Generate a directory and file structure diagram, including all files and directories."""
    structure = []

    def build_tree(dir_path, prefix=""):
        """Recursively build the directory tree."""
        try:
            entries = sorted(os.listdir(dir_path))
            for i, entry in enumerate(entries):
                full_path = os.path.join(dir_path, entry)
                is_last = (i == len(entries) - 1)

                # Check if the entry is excluded
                is_excluded = entry in EXCLUDE_DIRS or should_exclude_file(entry)

                # Add the current entry to the structure
                structure.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}{' [EXCLUDED]' if is_excluded else ''}")

                # Recursively add subdirectories
                if os.path.isdir(full_path):
                    build_tree(full_path, prefix + ("    " if is_last else "│   "))
        except Exception as e:
                structure.append(f"{prefix}Error reading directory: {e}")

    build_tree(root_dir)
    return "\n".join(structure)

def generate_html_version(project_dir, exclude_dirs, exclude_extensions):
    """Generate an HTML version of the project structure and file contents."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Structure</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
            .directory { margin-left: 20px; }
            .file { margin-left: 40px; }
            .file-content { margin-left: 60px; white-space: pre-wrap; background: #f4f4f4; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Project Structure</h1>
    """

    def list_files_and_directories(root_dir, exclude_dirs, exclude_extensions):
        """Recursively list all files and directories, excluding specified directories and files."""
        file_list = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Remove excluded directories from dirnames to prevent traversal
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            
            for filename in filenames:
                # Skip files with excluded extensions
                if any(filename.endswith(ext) for ext in exclude_extensions):
                    continue
                file_path = os.path.join(dirpath, filename)
                file_list.append(file_path)
        return file_list

    def read_file_contents(file_path):
        """Read the contents of a file, handling large files by streaming."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                return ''.join(file)
        except (IOError, UnicodeDecodeError) as e:
            return f"Error reading file: {e}"

    file_list = list_files_and_directories(project_dir, exclude_dirs, exclude_extensions)

    # Add project structure to HTML
    for dirpath, dirnames, filenames in os.walk(project_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        html_content += f'<div class="directory"><strong>📁 {os.path.basename(dirpath)}</strong></div>'
        for filename in filenames:
            if any(filename.endswith(ext) for ext in exclude_extensions):
                continue
            html_content += f'<div class="file">📄 {filename}</div>'
            file_path = os.path.join(dirpath, filename)
            file_content = read_file_contents(file_path)
            html_content += f'<div class="file-content">{file_content}</div>'

    html_content += "</body></html>"
    return html_content

def split_content(content, lines_per_file=2000):
    """Split content into chunks of a specified number of lines."""
    lines = content.splitlines()
    chunks = [lines[i:i + lines_per_file] for i in range(0, len(lines), lines_per_file)]
    return ["\n".join(chunk) for chunk in chunks]

def create_super_file(root_dir, super_file_name='master_file.txt', lines_per_file=2000):
    """Create a super file containing all files in the project, split into smaller chunks."""
    super_file_path = os.path.join(root_dir, super_file_name)
    
    # Check if the super file already exists
    if os.path.exists(super_file_path):
        # Ask the user if they want to overwrite or change the filename
        st.warning(f"The file '{super_file_name}' already exists.")
        overwrite = st.radio(
            f"Do you want to overwrite '{super_file_name}' or change the filename?",
            options=["Overwrite", "Change Filename"],
            index=0
        )
        
        if overwrite == "Change Filename":
            new_filename = st.text_input("Enter a new filename (without extension):", value=super_file_name)
            if new_filename:
                super_file_path = os.path.join(root_dir, new_filename)
            else:
                st.error("Please provide a valid filename.")
                return
        else:
            st.info(f"Overwriting '{super_file_name}'.")
    
    # Find the README file (if any)
    readme_files = [f for f in os.listdir(root_dir) if f.lower().startswith('readme')]
    readme_content = ""
    
    if readme_files:
        readme_path = os.path.join(root_dir, readme_files[0])  # Use the first README file found
        readme_content, _ = read_file_contents(readme_path)
    
    # Build the content
    content = []
    if readme_content:
        content.append("===== README =====\n")
        content.append(readme_content + "\n\n")
    
    # Add the directory and file structure diagram
    content.append("===== PROJECT STRUCTURE =====\n")
    structure_diagram = generate_structure_diagram(root_dir)
    content.append(structure_diagram + "\n\n")
    
    # Add all files, excluding sensitive files and other excluded files
    content.append("===== FILE DETAILS =====\n")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove excluded directories from dirnames to prevent traversal
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(file_path, root_dir)
            
            # Skip sensitive files entirely
            if filename in SENSITIVE_FILES:
                continue
            
            # Get file metadata
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(filename)[1]
            
            # Write file metadata
            content.append(f"===== FILE: {relative_path} =====\n")
            content.append(f"Name: {filename}\n")
            content.append(f"Size: {file_size} bytes\n")
            content.append(f"Extension: {file_ext}\n")
            
            # Check if the file should be excluded
            if should_exclude_file(filename):
                content.append("Status: Excluded (content not included)\n\n")
            else:
                # Read file contents
                contents, is_binary_file = read_file_contents(file_path)
                content.append(f"Type: {'Binary (Base64)' if is_binary_file else 'Text'}\n")
                content.append(f"Size: {len(contents)}\n\n")
                content.append(contents + "\n\n")
    
    # Join the content into a single string
    full_content = "\n".join(content)
    
    # Split the content into chunks
    chunks = split_content(full_content, lines_per_file)
    
    # Save each chunk as a separate file
    for i, chunk in enumerate(chunks):
        chunk_filename = f"{super_file_name.split('.')[0]}_{i + 1}.txt"
        chunk_path = os.path.join(root_dir, chunk_filename)
        with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
            chunk_file.write(chunk)
        st.success(f"Chunk {i + 1} created at: {chunk_path}")
        
        # Provide a download button for each chunk
        with open(chunk_path, 'r') as file:
            st.download_button(
                label=f"Download {chunk_filename}",
                data=file.read(),
                file_name=chunk_filename,
                mime="text/plain"
            )

def main():
    # Set page configuration with a modern, futuristic theme
    st.set_page_config(
        page_title="Project Code Fusion", 
        page_icon="🚀", 
        layout="wide"
    )

    # Custom CSS for improved readability and spacing
    st.markdown("""
    <style>
    /* Reduce space between nav bar and heading */
    h1 {
        margin-top: 0 !important; /* Remove top margin */
        padding-top: 0 !important; /* Remove top padding */
    }

    /* General app styling */
    .stApp {
        background-color: #f0f2f6; /* Light gray background for better contrast */
        color: #333333; /* Dark gray text for better readability */
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #cccccc;
        font-size: 16px;
    }

    /* Buttons */
    .stButton > button {
        background-color: #4a90e2;
        color: white;
        border: none;
        font-size: 16px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #5fa5ff;
        transform: scale(1.05);
    }

    /* Headings and explanatory text */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #4a90e2; /* Blue headings */
    }
    .explanatory-text {
        font-size: 18px !important;
        color: #333333 !important;
        line-height: 1.6;
    }

    /* Radio button labels */
    .stRadio > label {
        font-size: 18px !important;
        color: #333333 !important;
        margin-bottom: 10px;
    }

    /* Advanced settings expander */
    .stExpander {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .stExpander label {
        font-size: 16px !important;
        color: #333333 !important;
    }

    /* Checkboxes */
    .stCheckbox > label {
        font-size: 16px !important;
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title with a futuristic aesthetic
    st.markdown("<h1 style='text-align: center; color: #4a90e2;'>🚀 Project Code Fusion</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666666;'>Transform Your Project into a Comprehensive XML, HTML, or Markdown Snapshot</p>", unsafe_allow_html=True)

    # Project directory selection
    st.markdown("""
    <div class="explanatory-text">
        ### 📂 Select Project Directory
        Enter the full path to your project directory. This is where the tool will look for files to include in the output.
    </div>
    """, unsafe_allow_html=True)
    project_dir = st.text_input("Enter full path to project directory", placeholder="/path/to/your/project")

    # Advanced options with expandable section
    with st.expander("🔧 Advanced Configuration", expanded=False):  # Collapsed by default
        # Use columns for a professional layout
        col1, col2 = st.columns(2)

        with col1:
            # Common directories to exclude
            st.markdown("**Common Directories:**")
            exclude_dirs_options = [
                ".git", "node_modules", "venv", "__pycache__", "dist", "build", 
                "logs", "temp", "cache", "bin", "obj", "vendor"
            ]
            exclude_dirs = []
            for dir_name in exclude_dirs_options:
                if st.checkbox(f"Exclude directory: `{dir_name}`", value=True, key=f"dir_{dir_name}"):
                    exclude_dirs.append(dir_name)

        with col2:
            # Common file extensions to exclude
            st.markdown("**Common File Extensions:**")
            exclude_extensions_options = [
                ".log", ".tmp", ".bak", ".swp", ".pyc", ".class", ".jar", 
                ".war", ".tar.gz", ".zip", ".png", ".jpg", ".gif", ".ico"
            ]
            exclude_extensions = []
            for ext in exclude_extensions_options:
                if st.checkbox(f"Exclude file extension: `{ext}`", value=True, key=f"ext_{ext}"):
                    exclude_extensions.append(ext)

        # Allow users to upload a CSV for custom exclusions
        st.markdown("### Add Custom Exclusions via CSV")
        uploaded_file = st.file_uploader("Upload a CSV file with custom exclusions (columns: 'type', 'value')", type=["csv"])
        if uploaded_file is not None:
            try:
                custom_exclusions = pd.read_csv(uploaded_file)
                if not set(custom_exclusions.columns) >= {"type", "value"}:
                    st.error("CSV must contain 'type' and 'value' columns.")
                else:
                    for _, row in custom_exclusions.iterrows():
                        if row["type"] == "dir":
                            exclude_dirs.append(row["value"])
                        elif row["type"] == "ext":
                            exclude_extensions.append(row["value"])
                        elif row["type"] == "pattern":
                            EXCLUDE_PATTERNS.append(row["value"])
                    st.success("Custom exclusions added successfully!")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

        # Output filename
        output_filename = st.text_input(
            "Output Filename (without extension)", 
            value="master_file", 
            placeholder="master_file"
        )

    # Generate options
    st.markdown("""
    <div class="explanatory-text">
        ### 🛠️ Generate Output
        Choose the format for your output file. Each format is optimized for a specific use case:
    </div>
    """, unsafe_allow_html=True)

    # Update the radio button labels
    output_format = st.radio(
        "Select output format:",
        options=[
            "XML (for AI/ML)",
            "HTML (for humans)",
            "Markdown (for documentation)"
        ],
        key="output_format"
    )

    if st.button("🌟 Generate Output"):
        if not project_dir:
            st.error("Please provide a project directory path.")
            return

        if not os.path.isdir(project_dir):
            st.error(f"The directory '{project_dir}' does not exist. Please provide a valid path.")
            return

        try:
            if output_format == "XML (for AI/ML)":
                # Generate XML output
                create_super_file(project_dir, f"{output_filename}.xml")
            elif output_format == "HTML (for humans)":
                # Generate HTML output
                html_content = generate_html_version(project_dir, exclude_dirs, exclude_extensions)
                st.success(f"✨ HTML Generated Successfully!")
                
                # Option to download the HTML file
                st.download_button(
                    label="Download HTML",
                    data=html_content,
                    file_name=f"{output_filename}.html",
                    mime="text/html"
                )
            else:
                # Generate Markdown output
                create_super_file(project_dir, f"{output_filename}.md")

        except Exception as e:
            st.error(f"Error generating output: {e}")

    # Explanatory section
    st.markdown("---")
    st.markdown("""
    ### 🤖 How It Works
    - Select your project directory
    - Customize exclusions (optional)
    - Choose between XML (for AI/ML), HTML (for humans), or Markdown (for documentation)
    - Click 'Generate Output'
    - Get a comprehensive snapshot of your project
    """)

if __name__ == "__main__":
    main()