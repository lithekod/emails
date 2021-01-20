from dataclasses import dataclass
from typing import List
from sys import argv, exit
from functools import reduce
import re


@dataclass
class Point:
    heading: str
    content: str


@dataclass
class Section:
    intro: str
    points: List[Point]


def parse(string):
    """Parses a string and converts it to Sections and Points."""
    section = re.compile(":([A-Z]*):(.*?)(?=:[A-Z]*:)",
                         flags=re.DOTALL | re.MULTILINE)

    se = Section("", [])
    en = Section("", [])
    active_section = None

    content = string + ":END:"
    for match in re.finditer(section, content):
        start, body = match.groups()
        body = body.strip()
        if start == "SE":
            active_section = se
            continue

        if start == "EN":
            active_section = en
            continue

        if start == "INTRO":
            active_section.intro = body
            continue

        if start == "POINT":
            intro, body = body.split("\n", 1)
            active_section.points.append(Point(intro, body))
            continue

        print("Error!")

    return se, en


def format(section):
    """Formats a section to a html string."""
    def format_point(point):
        content = point.content.replace(
                "\n\n",
                "\n</p><p class='point-section'>\n")
        out = f"<h2 class='point-heading'>{point.heading}</h2>\n"
        out += f"<p class='point-section'>{content}</p>"
        return out

    if len(section.intro) > 0:
        intro = f"<p class='intro'>{section.intro}</p>"
    else:
        intro = ""

    return (intro, "\n".join(map(format_point, section.points)))


def format_file(path, template):
    """Parses a file and formats it to html."""
    se, en = parse(open(path).read())

    sections = open(template).read().split("-----")
    content = [*format(se), *format(en), ""]
    result = reduce(lambda x, y: x + y[0] + y[1],
                    zip(sections, content),
                    "")
    return result


if __name__ == "__main__":
    try:
        _, path = argv
    except IndexError:
        print("Expected a valid file")
        exit(1)
    else:
        print(format_file(path, "template.html"))
