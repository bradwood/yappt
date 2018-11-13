from yappt.validator_mixins import KeyExistsMixIn, ValIsStrMixIn, ValIsDictMixIn, ValIsDictWithSubKeysMixIn
from ruamel.yaml import YAML
from yappt.exceptions import LayoutError, SlideError, ContentError


class Foo(ValIsDictWithSubKeysMixIn):
    def __init__(self, payload, *args, **kwargs):
        super().__init__(payload, *args, **kwargs)
        print(payload)



yaml_str = """
---
metadata:
  title: This is the title of my presentation
  author: 'Bradley Wood <brad@bradleywood.com>'
  date: 2018-11-05


settings:
  pagenum: true  # `n / m` in bottom right
  titlebar: false # `presentation title` at top centre
  incremental: true # turn on incremental rendering of slide elements

"""

yaml = YAML()

data = yaml.load(yaml_str)

f = Foo(data, _key='metadata', _exception=ContentError, _elem='settings', _sub_keys=['title', 'author'])

