<img src='yappt.png' align='center' width='100%'>


YAPPT is quite literally, *Yet Another Powerpoint Tool*. It's another one of those tools that, for some reason, geeks and coders think is a good way of presenting stuff to fellow geeks.

But, *YAPPT Ain't Powerpoint*, nor is it like any other terminal-based presentation tools I've found.


[![asciicast](https://asciinema.org/a/pmUj5xUlEpIdmkg5hQiYtc3WP.svg)](https://asciinema.org/a/pmUj5xUlEpIdmkg5hQiYtc3WP)

## What's so special about this one, then?

Here's a list of features:

* supports slide layouts reasonably well, with the ability to split the screen up into cells and drop bits of content into these cells in a sane way, which aligns stuff well -- this was the feature I wanted but couldn't find in other tools.
* supports figlet fonts natively, because true geeks **need** figlet support
* markdown support is built in (but code-based syntax highlighting is still a to-do)
* all the colors your terminal supports
* emojis and unicode as standard 🤘🏼
* left, centre and right justifying text blocks
* dynamically redraw the slide if the terminal's dimensions changes
* reload the input file to the slide you're on without restarting
* slide by slide, or cell by cell transitions
* input is a simple YAML file

## Requirements (and config that works for me):

* Python 3.6 (yes, I've not tested it on anything older, but it works with this. It'll probably work with most other Python3 versions)
* `TERM=xterm-256color`
* curses/ncurses

## Installation

`pip install git+https://gitlab.com/bradwood/yappt`

## Input
Input is YAML. See [INPUT.md](INPUT.md) for details.

## Issues and outstanding tasks

There are a few... chiefly because I hacked this thing together for my own use, rather than aspiring to build anything like hardened production-ready software.

### Test coverage
Right now, it's pretty much non-existent. It works for me and, if it works for you too then I'll be pleased. I may add some tests when time/inclination permits, but for now, it is what it is.

I've manually tested it only on MacOS running under iTerm2. YMMV if you try it under another terminal client or setup. Raise an issue if you wish to, but please do-so on [GitLab](https://gitlab.com/bradwood/yappt) and nowhere else.

### Todo

* syntax highlighting code blocks
* add better version management.
* template support (i.e., set the template for all slides and then inherit)
* including multiple YAML files
* er... tests...
* tox

## Contributions...

...are welcome. Fork, tweak, merge request, etc... But please do this on [GitLab](https://gitlab.com/bradwood/yappt) and nowhere else -- thanks!

## Licence

[MIT](LICENSE)

## Credits

* cli library: [click](https://click.palletsprojects.com/en/7.x/)
* YAML library: [ruamel-yaml](https://yaml.readthedocs.io/en/latest/)
* figlet library: [pyfiglet](https://github.com/pwaller/pyfiglet)
* markdown library: [mistletoe](https://github.com/miyuchina/mistletoe)
