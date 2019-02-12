from enum import Enum


class SelectorType(Enum):
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"
    ID = "id"
    LINK_TEXT = "link text"
    NAME = "name"
    PARTIAL_LINK_TEXT = "partial link text"
    TAG_NAME = "tag name"
    XPATH = "xpath"
