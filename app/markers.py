def read_marker_section(file_path):
    """Reads the marker section content from a file.

    This is the Python implementation of the marker section technique that we
    use in our bash scripts; for reference, see:
        /opt/tinypilot-privileged/scripts/lib/markers.sh

    Args:
        file_path: the target file path as str.

    Returns:
        List of str
    """
    in_marker_section = False
    marker_section_lines = []
    with open(file_path, encoding='utf-8') as file:
        for line in file:
            content = line.strip()
            if content == '# --- AUTOGENERATED BY TINYPILOT - START ---':
                in_marker_section = True
                continue
            if content == '# --- AUTOGENERATED BY TINYPILOT - END ---':
                in_marker_section = False
                continue
            if in_marker_section:
                marker_section_lines.append(content)
    return marker_section_lines
