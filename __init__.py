from pipydash import PiPyDash

if __name__ == '__main__':
    config_file_path = 'config.yaml'
    _pipydash = PiPyDash()
    _pipydash.set_config(_pipydash.read_config_file(config_file_path))
    _pipydash.main()
