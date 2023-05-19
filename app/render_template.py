import jinja2
import yaml


def render(default_settings, user_overrides_file, template_file):
    user_overrides = yaml.safe_load(user_overrides_file.read()) or {}

    # Merge defaults with user-defined overrides.
    merged_settings = {**default_settings, **user_overrides}

    return jinja2.Environment().from_string(
        template_file.read()).render(merged_settings)
