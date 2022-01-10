from enum import Enum

WEB_ELEMENT = "element-6066-11e4-a52e-4f735466cecf"

STATUS_SUCCESS = 0


class SelectorType(Enum):
    css_selector = "css selector"
    link_text = "link text"
    partial_link_text = "partial link text"
    tag_name = "tag name"
    xpath = "xpath"


class WindowType(Enum):
    tab = "tab"
    window = "window"
