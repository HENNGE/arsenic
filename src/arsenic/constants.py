from enum import Enum

WEB_ELEMENT = "element-6066-11e4-a52e-4f735466cecf"


class SelectorType(Enum):
    class_name = "class name"
    css_selector = "css selector"
    id = "id"
    link_text = "link text"
    name = "name"
    partial_link_text = "partial link text"
    tag_name = "tag name"
    xpath = "xpath"
