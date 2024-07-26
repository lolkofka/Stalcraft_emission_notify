import glob
import importlib.util
import logging
import os

from config import config


def load_dynamics(folder: str):
    src_path = os.path.abspath(__file__).replace(f'{os.path.sep}{__name__}.py', '')
    logging.info('Loader source path: %s', src_path)
    dynamic_path = os.path.sep.join([src_path, folder])
    logging.info('Loader dynamics path: %s', dynamic_path)
    files = glob.glob(os.path.sep.join([dynamic_path, '**', '*']), recursive=True)
    files = [x for x in files if os.path.isfile(x) and x.endswith('.py')]
    loaded = 0

    for file in files:
        try:
            module_name = file.replace(f'{src_path}{os.path.sep}', '').replace('.py', '').replace(os.path.sep, '.')

            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded += 1
        except Exception as exception:
            logging.error('Failed to load %s', file)
            logging.error(exception)
            if config['bot']['debug']:
                raise exception
    logging.info('Loaded: %d/%d', loaded, len(files))
