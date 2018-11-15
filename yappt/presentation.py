"""Create Presentation objects from YAML input"""
from typing import List, Tuple
import logging
from datetime import date

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

from .exceptions import YAMLParseError, MetaDataError, SettingsError
from .metasettings import MetaData, Settings
from .slide import Slide

yaml = YAML()

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.DEBUG, filename='yappt.log',
                    format=logformat)  # datefmt="%Y-%m-%d %H:%M:%S"

LOGGER = logging.getLogger(__name__)

def process_yaml(filename) -> Tuple[MetaData, Settings, List[Slide]]:
    """Generate settings, metadata and Slides from input."""
    try:
        pres_dict = yaml.load(filename.read())
        LOGGER.debug("Loaded YAML")
    except (ScannerError, ParserError) as exc:
        yp = YAMLParseError(f'Could not load presentation: {filename.name}.')
        yp.show()
        print(exc)
        quit(yp.exit_code)

    metadata = MetaData(pres_dict,
                        _key='metadata',
                        _exception=MetaDataError,
                        _elem='YAML file',
                        _keys_from=['title', 'author', 'date'],
                        _type_list=[str, str, date],
                        )

    LOGGER.debug("Loaded metadata")

    settings = Settings(pres_dict,
                        _key='settings',
                        _exception=SettingsError,
                        _elem='YAML file',
                        _keys_from=['pagenum', 'titlebar', 'authorfooter', 'incremental', 'h_margin', 'v_margin'],
                        _type_list=[bool, bool, bool, bool, int, int],
                        )

    LOGGER.debug("Loaded settings")

    slides = []
    # load each slide into a slide list for later processing.
    # this relies on 3.7's ordered dicts by default.
    for s_name, s_data in \
            {k: v for k, v in pres_dict.items() if k not in ['metadata', 'settings']}.items():
        slides.append(Slide(s_name, s_data, settings, metadata))

    LOGGER.debug("Created slide list")
    return metadata, settings, slides
