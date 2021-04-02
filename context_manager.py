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


def get_social():
    try:
        soc = get_data()["website_configuration"]
        return dict(social={"twitter": soc["twitter_link"],
                            "facebook": soc["facebook_link"],
                            "github": soc["github_link"],
                            "youtube": soc["youtube_link"],
                            "linkedin": soc["linkedin_link"],
                            "instagram": soc["instagram_link"],
                            "dev": soc["dev_link"],
                            "whatsapp": soc["whatsapp_link"],
                            "reddit": soc["reddit_link"],
                            "pinterest": soc["pinterest_link"],
                            "telegram": soc["telegram_link"]})
    except KeyError:
        return dict(social={"twitter": "https://www.twitter.com",
                            "github": "https://www.github.com",
                            "facebook": "https://www.github.com",
                            "instagram": "https://www.instagram.com",
                            "youtube": "https://www.youtube.com",
                            "linkedin": "https://www.linkedin.com",
                            "dev": "https://dev.to",
                            "whatsapp": "https://www.whatsapp.com",
                            "reddit": "https://www.reddit.com",
                            "pinterest": "https://www.pinterest.com",
                            "telegram": "https://www.telegram.com"})


def newsletter_functionality(configuration=None):
    try:
        config_data = get_data()["newsletter_configuration"]
    except KeyError:
        enabled = False
    else:
        try:
            enabled = config_data["enabled"]
        except KeyError:
            enabled = False
    return dict(newsletter_enabled=enabled) if not configuration else enabled
