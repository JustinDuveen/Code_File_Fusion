import streamlit as st
import os
import base64
import re
import pandas as pd
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

# Configure default encoding for the script
sys.stdout.reconfigure(encoding='utf-8')

# Type aliases for clarity
FileContent = Tuple[str, bool]  # (content, is_binary)
ChunkList = List[str]

# Constants
EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', 'node_modules', 'dist', 'build', 'models', 'embeddings', 'checkpoints'}
EXCLUDE_EXTENSIONS = {'.pyc', '.log', '.tmp', '.cache', '.pkl', '.DS_Store', '.onnx', '.bin', '.pt', '.h5', 
                     '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.xls', '.pdf'}
EXCLUDE_PATTERNS = [r'bert', r'all-mini-lm', r'\.onnx$', r'\.bin$', r'\.pt$', r'\.h5$']
SENSITIVE_FILES = {'.env', 'secrets.json', 'config.yml'}


class FileHandler:
    @staticmethod
    def is_binary(file_path: str) -> bool:
        """Check if a file is binary by reading a small chunk and checking for null bytes."""
        try:
            chunk_size = 1024
            with open(file_path, 'rb') as f:
                chunk = f.read(chunk_size)
                return b'\x00' in chunk
        except Exception:
            return True

    @staticmethod
    def should_exclude_file(file_name: str) -> bool:
        """Check if a file should be excluded based on its name or pattern."""
        if file_name in SENSITIVE_FILES:
            return True
        
        if any(file_name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
            return True
        
        if any(re.search(pattern, file_name, re.IGNORECASE) for pattern in EXCLUDE_PATTERNS):
            return True
        
        return False

    @staticmethod
    def read_file_contents(file_path: str) -> FileContent:
        """Read file contents with proper encoding handling."""
        try:
            if FileHandler.is_binary(file_path):
                with open(file_path, 'rb') as file:
                    return base64.b64encode(file.read()).decode('utf-8'), True
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read(), False
            except UnicodeDecodeError:
                with open(file_path, 'rb') as file:
                    return file.read().decode('utf-8', errors='replace'), False
        except Exception as e:
            return f"Error reading file: {str(e)}", False

class ProjectStructure:
    @staticmethod
    def generate_structure_diagram(root_dir: str) -> str:
        """Generate a directory and file structure diagram."""
        structure = []

        def build_tree(dir_path: str, prefix: str = "") -> None:
            try:
                entries = sorted(os.listdir(dir_path))
                for i, entry in enumerate(entries):
                    full_path = os.path.join(dir_path, entry)
                    is_last = (i == len(entries) - 1)
                    is_excluded = entry in EXCLUDE_DIRS or FileHandler.should_exclude_file(entry)
                    
                    structure.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}"
                                   f"{' [EXCLUDED]' if is_excluded else ''}")
                    
                    if os.path.isdir(full_path):
                        build_tree(full_path, prefix + ("    " if is_last else "│   "))
            except Exception as e:
                structure.append(f"{prefix}Error reading directory: {str(e)}")

        build_tree(root_dir)
        return "\n".join(structure)

    @staticmethod
    def generate_html_version(project_dir: str, exclude_dirs: List[str], exclude_extensions: List[str]) -> str:
        """Generate an HTML version of the project structure."""
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

        for dirpath, dirnames, filenames in os.walk(project_dir):
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            rel_path = os.path.relpath(dirpath, project_dir)
            if rel_path != '.':
                html_content += f'<div class="directory"><strong>📁 {rel_path}</strong></div>'
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in exclude_extensions):
                    continue
                if filename in SENSITIVE_FILES:
                    continue
                
                file_path = os.path.join(dirpath, filename)
                html_content += f'<div class="file">📄 {filename}</div>'
                content, is_binary = FileHandler.read_file_contents(file_path)
                if not is_binary:
                    html_content += f'<div class="file-content">{content}</div>'

        html_content += "</body></html>"
        return html_content

class ContentGenerator:
    @staticmethod
    def split_content(content: str, lines_per_file: int = 2000) -> ChunkList:
        """Split content into chunks."""
        lines = content.splitlines()
        chunks = [lines[i:i + lines_per_file] for i in range(0, len(lines), lines_per_file)]
        return ["\n".join(chunk) for chunk in chunks]

    @staticmethod
    def create_super_file(root_dir: str, output_format: str, super_file_name: str = 'master_file.txt',
                         exclude_dirs: List[str] = None, exclude_extensions: List[str] = None) -> None:
        """Create output file in specified format."""
        if exclude_dirs is None:
            exclude_dirs = list(EXCLUDE_DIRS)
        if exclude_extensions is None:
            exclude_extensions = list(EXCLUDE_EXTENSIONS)

        try:
            if output_format == "HTML (for humans)":
                html_content = ProjectStructure.generate_html_version(root_dir, exclude_dirs, exclude_extensions)
                st.success("✨ HTML Generated Successfully!")
                st.download_button(
                    label="Download HTML",
                    data=html_content,
                    file_name=f"{super_file_name}.html",
                    mime="text/html"
                )
                return

            # Handle XML and Markdown formats
            content = []
            readme_files = list(Path(root_dir).glob('README*'))
            if readme_files:
                readme_content, _ = FileHandler.read_file_contents(str(readme_files[0]))
                content.extend(["===== README =====\n", readme_content + "\n\n"])

            content.extend([
                "===== PROJECT STRUCTURE =====\n",
                ProjectStructure.generate_structure_diagram(root_dir) + "\n\n",
                "===== FILE DETAILS =====\n"
            ])

            for dirpath, dirnames, filenames in os.walk(root_dir):
                dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
                
                for filename in filenames:
                    if filename in SENSITIVE_FILES:
                        continue
                        
                    file_path = Path(dirpath) / filename
                    relative_path = file_path.relative_to(root_dir)
                    
                    content.extend([
                        f"===== FILE: {relative_path} =====\n",
                        f"Name: {filename}\n",
                        f"Size: {file_path.stat().st_size} bytes\n",
                        f"Extension: {file_path.suffix}\n"
                    ])
                    
                    if FileHandler.should_exclude_file(filename):
                        content.append("Status: Excluded (content not included)\n\n")
                        continue
                    
                    file_content, is_binary = FileHandler.read_file_contents(str(file_path))
                    content.extend([
                        f"Type: {'Binary (Base64)' if is_binary else 'Text'}\n",
                        f"Content Length: {len(file_content)}\n\n",
                        file_content + "\n\n"
                    ])

            full_content = "\n".join(content)
            chunks = ContentGenerator.split_content(full_content)

            for i, chunk in enumerate(chunks, 1):
                ext = '.xml' if output_format == "XML (for AI/ML)" else '.md'
                chunk_filename = f"{super_file_name}_{i}{ext}"
                chunk_path = Path(root_dir) / chunk_filename
                
                try:
                    chunk_path.write_text(chunk, encoding='utf-8', errors='replace')
                    st.success(f"Chunk {i} created at: {chunk_path}")
                    
                    st.download_button(
                        label=f"Download {chunk_filename}",
                        data=chunk.encode('utf-8'),
                        file_name=chunk_filename,
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error saving chunk {i}: {str(e)}")

        except Exception as e:
            st.error(f"Error generating output: {str(e)}")
            st.error(f"System encoding: {sys.getdefaultencoding()}")
            st.error(f"Filesystem encoding: {sys.getfilesystemencoding()}")

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Project Code Fusion",
        page_icon="🚀",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
    <style>
    h1 { margin-top: 0 !important; padding-top: 0 !important; }
    .stApp {
        background-color: #f0f2f6;
        color: #333333;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #cccccc;
        font-size: 16px;
    }
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
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #4a90e2;
    }
    .explanatory-text {
        font-size: 18px !important;
        color: #333333 !important;
        line-height: 1.6;
    }
    .stRadio > label {
        font-size: 18px !important;
        color: #333333 !important;
        margin-bottom: 10px;
    }
    .stExpander {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .stCheckbox > label {
        font-size: 16px !important;
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown(
        "<h1 style='text-align: center; color: #4a90e2;'>🚀 Project Code Fusion</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: #666666;'>Transform Your Project into a Comprehensive XML, HTML, or Markdown Snapshot</p>",
        unsafe_allow_html=True
    )

    # Project directory selection
    st.markdown("""
    <div class="explanatory-text">
        ### 📂 Select Project Directory
        Enter the full path to your project directory. This is where the tool will look for files to include in the output.
    </div>
    """, unsafe_allow_html=True)
    
    project_dir = st.text_input(
        "Enter full path to project directory",
        placeholder="/path/to/your/project"
    )

    # Advanced configuration
    with st.expander("🔧 Advanced Configuration", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Common Directories:**")
            exclude_dirs = []
            for dir_name in sorted(EXCLUDE_DIRS):
                if st.checkbox(f"Exclude directory: `{dir_name}`", value=True, key=f"dir_{dir_name}"):
                    exclude_dirs.append(dir_name)

        with col2:
            st.markdown("**Common File Extensions:**")
            exclude_extensions = []
            for ext in sorted(EXCLUDE_EXTENSIONS):
                if st.checkbox(f"Exclude file extension: `{ext}`", value=True, key=f"ext_{ext}"):
                    exclude_extensions.append(ext)

        # Custom exclusions via CSV
        st.markdown("### Add Custom Exclusions via CSV")
        uploaded_file = st.file_uploader(
            "Upload a CSV file with custom exclusions (columns: 'type', 'value')",
            type=["csv"]
        )
        
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

    # Generate options (continued)
    st.markdown("""
    <div class="explanatory-text">
        ### 🛠️ Generate Output
        Choose the format for your output file. Each format is optimized for a specific use case:
        - XML: Optimized for AI/ML processing
        - HTML: Human-readable web format
        - Markdown: Documentation-friendly format
    </div>
    """, unsafe_allow_html=True)

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
            ContentGenerator.create_super_file(
                root_dir=project_dir,
                output_format=output_format,
                super_file_name=output_filename,
                exclude_dirs=exclude_dirs,
                exclude_extensions=exclude_extensions
            )
        except Exception as e:
            st.error(f"Error generating output: {str(e)}")
            st.error(f"System encoding: {sys.getdefaultencoding()}")
            st.error(f"Filesystem encoding: {sys.getfilesystemencoding()}")

    # Help section
    st.markdown("---")
    with st.expander("ℹ️ How to Use Project Code Fusion", expanded=False):
        st.markdown("""
        ### 🤖 Quick Guide
        1. **Select Directory**: Enter the full path to your project folder
        2. **Configure Options**: 
           - Use Advanced Configuration to customize exclusions
           - Upload a CSV file for custom exclusions
           - Choose your preferred output filename
        3. **Choose Format**:
           - XML: Best for AI/ML processing
           - HTML: Easy to read in a browser
           - Markdown: Perfect for documentation
        4. **Generate**: Click 'Generate Output' and download your files

        ### 💡 Tips
        - Exclude large binary files to reduce output size
        - Use HTML format for human review
        - Use XML format for AI processing
        - Use Markdown for documentation systems

        ### 🔒 Security
        - Sensitive files (.env, secrets.json, etc.) are automatically excluded
        - Binary files are encoded safely
        - Large files are split into manageable chunks
        """)

if __name__ == "__main__":
    main()