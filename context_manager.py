from data_manager import get_data
import datetime as dt


def get_name(configuration=None):
    data = get_data()
    try:
        return dict(name=data["website_configuration"]["name"]) if configuration is None else \
            data["website_configuration"]["name"]
    except (TypeError, IndexError, KeyError):
        return dict(name="Website") if configuration is None else data["website_configuration"]["name"]


def get_date():
    return dict(year=dt.datetime.now().year)


def get_background(configuration='website_configuration'):
    try:
        if configuration == 'website_configuration':
            return dict(background_image=get_data()[configuration]["background_image"])
        else:
            try:
                background = get_data()[configuration]["background_image"]
                if background == '':
                    return get_data()["website_configuration"]["background_image"]
                return background
            except (KeyError, TypeError):
                try:
                    return get_data()["website_configuration"]["background_image"]
                except (KeyError, TypeError):
                    return ''
    except (KeyError, TypeError):
        return dict(background_image="")


def get_navbar(configuration=None):
    try:
        return dict(navbar=get_data()["website_configuration"]["navigation_bar_color"]) if configuration is None else \
            get_data()["website_configuration"]["navigation_bar_color"]
    except (KeyError, TypeError):
        return dict(navbar='#FFFFFF') if configuration is None else '#FFFFFF'


def get_social():
    try:
        soc = get_data()["website_configuration"]
        return dict(social={"twitter": soc["twitter_link"],
                            "facebook": soc["facebook_link"],
                            "github": soc["github_link"],
                            "youtube": soc["youtube_link"],
                            "linkedin": soc["linkedin_link"],
                            "instagram": soc["instagram_link"],
                            "dev": soc["dev_link"]})
    except KeyError:
        return dict(social={"twitter": "https://www.twitter.com",
                            "github": "https://www.github.com",
                            "facebook": "https://www.github.com",
                            "instagram": "https://www.instagram.com",
                            "youtube": "https://www.youtube.com",
                            "linkedin": "https://www.linkedin.com",
                            "dev": "https://dev.to"})