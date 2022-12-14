from imports import *


def read_json(path=None):
    """Read json file and load content to dictionary"""
    with open(file=path, mode='r') as json_handle:
        return json.load(json_handle)


def write_json(path=None, content=None):
    """Write dictionary to json file"""
    with open(file=path, mode='w+') as json_handle:
        json.dump(content, json_handle, indent=4)
    return


def regenerate_full_archive(components_dir=None):
    """Combine the archives of each individual component"""
    full_archive = dict()
    for file in os.listdir(path=components_dir):
        json_path = os.path.join(components_dir, file)
        component_key = file.split('_', maxsplit=3)[-1].split('.')[0]
        full_archive[component_key] = read_json(path=json_path)
    write_json(path='full_archive.json', content=full_archive)
    return


def check_permissions():
    valid_cookie = False
    print(f'- {constants.ICON_COOKIE:2}Authenticating user...')
    while not valid_cookie:
        if os.path.exists(constants.COOKIES) and validate_cookie():
            valid_cookie = True
        elif os.path.exists(constants.COOKIES) and not validate_cookie():
            user_input = input(
                f'\tFile {constants.COOKIES} exists in the current working directory but it is outdated:\n'
                f'\t- Continue with current cookie {constants.ICON_ARROW} c\n'
                f'\t- Regenerate cookie {constants.ICON_ARROW} r\n'
                f'\t- Exit zbunchpload {constants.ICON_ARROW} e\n'
                f'\tPlease enter a selection (r/e): ')
            if user_input == 'r':
                valid_cookie = True if curl_cookie() else False
            elif user_input == 'e':
                exit(f'\tzbunchpload will now exit.')
        else:
            valid_cookie = curl_cookie()
    return


def curl_cookie():
    validation = False
    url = 'https://cpauth.icos-cp.eu/password/login'
    data = {'mail': input('\tPlease enter your e-mail: '),
            'password': getpass(prompt='\tPlease enter your password: ')}
    cookie_response = requests.post(url=url, data=data)
    if cookie_response.status_code == 200:
        validation = True
        save_cookie(cookie_response.cookies)
        validate_cookie()
    else:
        print('\tSomething went wrong. Please try again...')
    return validation


def validate_cookie():
    """Validate existing cookie."""
    validation = False
    url = 'https://cpauth.icos-cp.eu/whoami'
    cookie_validation_response = requests.get('https://cpauth.icos-cp.eu/whoami', cookies=load_cookie())
    if cookie_validation_response.status_code == 200:
        validation = True
        print(f'\t{constants.ICON_ARROW_DOWN_RIGHT} {constants.ICON_BABY} Hello '
              f'{cookie_validation_response.json()["email"]}!')
    return validation


def save_cookie(cookie_jar: requests.cookies.RequestsCookieJar = None):
    with open(constants.COOKIES, 'wb') as cookie_handle:
        pickle.dump(cookie_jar, cookie_handle)


def load_cookie():
    with open(constants.COOKIES, 'rb') as cookie_handle:
        return pickle.load(cookie_handle)


def parse_arguments(mode: str = None) -> dict:
    skipping_handlers = collections.OrderedDict({
        'archive_files': True,
        'fill_handlers': True,
        'try_ingest': True,
        'archive_json': True,
        'upload_metadata': True,
        'upload_data': True,
        'store_current_archive': True
    })
    print(f'- {constants.ICON_GEAR:3}Mode parsing ({mode})...')
    for handler, handler_items in zip(mode, skipping_handlers.items()):
        boolean_handler = bool(int(handler))
        print(f'\t{" ".join(handler_items[0].split("_")):21} =  {boolean_handler}')
        skipping_handlers[handler_items[0]] = bool(int(handler))
    return skipping_handlers


def find_files(search_string: str = None) -> list:
    split_search_string = search_string.rsplit('/', 1)
    directory = split_search_string[0]
    regex = split_search_string[1]
    pattern = re.compile(f'{regex}')
    found_files = list()
    for file_name in os.listdir(directory):
        if pattern.match(file_name):
            found_files.append(os.path.join(directory, file_name))
    return sorted(found_files)
