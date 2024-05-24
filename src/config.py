import re
import os
import sys
import json
import logging as log

log.basicConfig(
        level=log.DEBUG,
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(message)s'
)


class Config:
    def __init__(self):
        self.config = None
        self.raw_config = self._load_config_file()
        self.params = {}


    def get_raw_config(self):
        return self.raw_config


    def _load_config_file(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        path_components = script_dir.split(os.path.sep)
        if 'src' in path_components:
            src_index = path_components.index('src')
            path_components = path_components[:src_index]
        base_path = os.path.sep.join(path_components)
        path = os.path.join(base_path, 'athena.json')

        log.info(f"loading config file [{path}]")
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"could not locate config file [{path}]")
            sys.exit(1)


    def update_config_values(self):
        params = self.params
        def replace_placeholders(value, params):
            if isinstance(value, str):
                return re.sub(r'\{(.*?)\}', lambda m: params.get(m.group(1), m.group(0)), value)
            elif isinstance(value, dict):
                return {k: replace_placeholders(v, params) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_placeholders(elem, params) for elem in value]
            return value
        self.config = replace_placeholders(self.raw_config, params)


    def add_params_str(self, params_str):
        """params seperated by comma."""
        for param in params_str.split(","):
            key, value = param.split("=")
            self.params[key] = value

        # update config file with parameters
        self.update_config_values()
        return self.params

    
    def add_params_dict(self, params_dict):
        for key, value in params_dict.items():
            self.params[key] = value
        self.update_config_values()

    
    def add_params_arr(self, params_arr):
        for param in params_arr:
            key, value = param.split('=')
            self.params[key] = value
        self.update_config_values()


    def get_query_by_name(self, query_name):
        log.info("getting query by name")
        if query_name is None:
            query_name = "default"

        if 'queries' in self.config:
            for query_blob in self.config['queries']:
                if query_name == query_blob['name']:
                    log.info("\t%s", query_blob['value'])
                    log.info("")
                    return query_blob
        else:
            log.info('could not locate queries section in config file.')
        log.info("query not found [%s]", query_name)
        log.info("")
        return None


    def get_config(self):
        """return the full config after applying parameters"""
        return self.config


    def get_all_query_names(self):
        query_names = []
        for query in self.config['queries']:
            query_names.append(query['name'])
        return query_names

    
    def get_params(self):
        return self.params

    
    def set_default_config_params(self):
        config = self.get_config()
        if 'parameters' not in config:
            return

        log.info("")
        log.info("found parameters in config file")
        file_params = config['parameters']

        file_params_dict = {param['name']: param['value'] for param in file_params}

        self.params.update(file_params_dict)


    def set_query_obj_params(self, query_obj):
        return query_obj


    def get_colors(self):
        colors_config = next((item \
                for item in self.config['config'] if 'colors' in item), None)
        if colors_config:
            colors = colors_config['colors']
            return colors
        else:
            log.info("No colors found, using defaults.")
            return ["cyan", "magenta", "yellow"]


    def get_config_value(self, name):
        """Will search overrides first for the template, if it does not find anything"""
        """it will return just the config value it finds"""
        config = self.config
        for cfg in config['config']:
            if 'profile' in cfg:
                if cfg.get('profile') == self.params.get('profile') and \
                        cfg.get('region') == self.params.get('region'):
                    log.info("found [%s] [%s] override", cfg.get('profile'), cfg.get('region'))
                    for val in cfg.get('values'):
                        return val.get(name)
                elif cfg.get('profile') == self.params.get('profile'):
                    log.info("found [%s] override", cfg.get('profile'))
                    for val in cfg.get('values'):
                        return val.get(name)

        for cfg in config['config']:
            if 'name' in cfg and cfg['name'] == name:
                return cfg['value']
        return None
