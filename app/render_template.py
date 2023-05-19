import jinja2
import yaml


def render(default_settings, user_overrides_file, template_file):
    """Renders a Jinja2 template using TinyPilot settings.

    Args:
        default_settings: TODO
        user_overrides_file: TODO
        template_file: TODO

    Returns:
        A str representing the template rendered with the data.
    """
    # If the overrides file is empty, use an empty dict.
    user_overrides = yaml.safe_load(user_overrides_file.read()) or {}

    # Merge defaults with user-defined overrides. User-defined overrides take
    # precedence over the defaults.
    merged_settings = {**default_settings, **user_overrides}

    return jinja2.Environment().from_string(
        template_file.read()).render(merged_settings)
