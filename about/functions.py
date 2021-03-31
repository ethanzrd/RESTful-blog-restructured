from context_manager import get_background
from data_manager import get_data


def get_page_elements():
    try:
        about_config = get_data()['about_configuration']
    except KeyError:
        heading = "About us"
        subheading = "About what we do."
        content = "For now, this page remains empty."
        background_image = get_background()
    else:
        try:
            heading = about_config['page_heading']
            subheading = about_config['page_subheading']
            content = about_config['page_content']
            background_image = about_config["background_image"]
        except KeyError:
            heading = "About us"
            subheading = "About what we do."
            content = "For now, this page remains empty."
            background_image = get_background()
    return heading, subheading, content, background_image
