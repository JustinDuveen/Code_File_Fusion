# Code_File_Fusion 🚀

**Transform Complex Codebases into a Single, Analyzable XML File**

---

## What is Code_File_Fusion?

**Code_File_Fusion** is a powerful Python tool designed to simplify the analysis of complex codebases. It consolidates your entire project into a single, easily analyzable XML file, making it perfect for developers and AI models alike.

Whether you're reviewing a massive codebase or preparing it for AI analysis, **Code_File_Fusion** is your go-to solution.

---

## Key Features ✨

- **Instant Project Overview**: Generates a comprehensive XML snapshot of your project structure.
- **Effortless Code Analysis**: Combines all relevant file contents into one master file.
- **Smart Filtering**: Automatically excludes unnecessary files (e.g., `.git`, `venv`, logs, etc.).
- **Memory Efficient**: Streams large files to prevent memory overload.
- **Zero Dependencies**: Lightweight and easy to use—no external libraries required.

---

## Why Use Code_File_Fusion? 🚀

- **Simplify Complex Reviews**: Quickly understand large and complex projects.
- **AI-Ready Codebases**: Prepare your code for AI analysis with ease.
- **Lightning-Fast**: Optimized for speed and efficiency.
- **Open Source**: Free, transparent, and community-driven.

---

## Quick Start 🛠️

### Installation

No dependencies required! Just clone the repository:

```bash
git clone https://github.com/your-username/Code_File_Fusion.git
cd Code_File_Fusion
Basic Usage
Run the tool on your project:

bash
Copy
python create_master_file.py /path/to/your/project --output master_file.xml
Customize Exclusions
Exclude specific directories or file extensions:

bash
Copy
python create_master_file.py /path/to/project \
  --exclude-dirs .git venv \
  --exclude-extensions .log .tmp
Sample Output 📄
Here's what the generated XML looks like:

xml
Copy
<project>
  <structure>
    <directory name="src">
      <file name="main.py" />
      <file name="utils.py" />
    </directory>
  </structure>
  <file path="/project/src/main.py">
    <![CDATA[Project code contents]]>
  </file>
</project>
Run HTML
Ways to Contribute 🤝
We love contributions! Here's how you can help:

💻 Code Contributions: Open a Pull Request.

🐛 Report Issues: Submit bugs or feature requests on GitHub Issues.

💸 Financial Support: Help sustain the project with a donation.

Support the Project ☕
Your support keeps the project alive! Here are some suggested donation tiers:

🍵 $5: Buys a coffee to keep us coding.

🍽️ $10: Supports an hour of development.

🚀 $20: Helps maintain the project for the long term.

Donate via PayPal: [Donate Now](https://www.paypal.com/paypalme/justinduveen?country.x=ZA&locale.x=en_US)

License 📜

Code_File_Fusion is open-source and licensed under the MIT License. Feel free to use, modify, and share!

Thank You! 🙏

Thank you for using Code_File_Fusion! Your support and contributions make a huge difference. Let's build something amazing together! 🚀

![License](https://img.shields.io/badge/License-MIT-blue.svg)