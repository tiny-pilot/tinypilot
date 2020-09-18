import glob
import os


def all_frontend_files():
    return _find_files_by_pattern([
        ('./app/templates', '*.html'),
        ('./app/static/css', '*.css'),
        ('./app/static/js', '*.js'),
    ])


def custom_elements_files():
    return _find_files_by_pattern([
        ('./app/templates/custom-elements', '*.html'),
    ])


def _find_files_by_pattern(patterns):
    files = []
    for pattern in patterns:
        path_root, glob_pattern = pattern
        files.extend([
            y for x in os.walk(path_root)
            for y in glob.glob(os.path.join(x[0], glob_pattern))
        ])
    return files
