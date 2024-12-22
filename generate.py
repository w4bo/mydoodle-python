# Split the file content based on the delimiter "---username---"
import re
from pathlib import Path

with open("report.txt", "r", encoding="utf-8") as file:
    file_content = file.read()
    sections = re.split(r"(?=---.+?---)", file_content.strip())

    # Process each section and save to a markdown file
    output_dir = Path(".")
    output_dir.mkdir(exist_ok=True)

    for section in sections:
        # Extract the username from the section
        match = re.search(r"---(.+?)---", section)
        if match:
            username = match.group(1).strip().replace(" ", "_")
            filename = f"{username}.md"
            # Save the section content to a file
            file_path = output_dir / filename
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(section.strip())

    # List the generated files for verification
    output_files = list(output_dir.glob("*.md"))
    print(output_files)

    # Rewrite the files, removing the "---username---" lines from the content.
    for file_path in output_files:
        # Read the content of the file
        with open(file_path, "r", encoding="utf-8") as file2:
            content = file2.read()
        # Remove the "---username---" line
        updated_content = re.sub(r"---.+?---\n", "", content, count=1)
        # Write back the updated content
        with open(file_path, "w", encoding="utf-8") as file2:
            file2.write(updated_content)

    # Verify the updated content
    updated_files = {file.name: file.read_text() for file in output_files}
    updated_files
