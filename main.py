import requests
import base64
import json
import os
import time
import yaml
import re


def read_config(yaml_path: str):
    """Reads a yaml file to get config for the project

    :param yaml_path: path tp yaml config file
    :type yaml_path: str
    :return: contents of config file
    :rtype: dict
    """
    with open(yaml_path, 'r') as stream:
        return yaml.safe_load(stream)


def img_to_json(folder_path: str, file_name: str):
    """Opens image as bytes and then encodes in base64 to send in a POST request

    :param folder_path: path to a file
    :type folder_path: str
    :param file_name: name of a file
    :type file_name: str
    :return: encoded image
    :rtype: byte64?
    """
    image_file = os.path.join(folder_path, file_name)
    with open(image_file, "rb") as f:
        im_bytes = f.read()

    return base64.b64encode(im_bytes).decode("utf8")


def get_images(config):
    """Find all images in supplied directory that match the file types in the config open as bytes and store with an
    id and their filename

    :param config: config for project
    :type config: dict
    :return: files with encoded data
    :rtype: dict
    """
    # regex pattern for matching to file extensions in config file
    # should only use this way for trusted files
    pattern = f"(?i)^.+\.({'|'.join([e for e in config['image_extensions']])})$"

    return {count: {'filename': f, 'image': img_to_json(config['file_dir'], f)} for count, f in
            enumerate(os.listdir(config['file_dir'])) if re.match(pattern, f)}


def main():
    config = read_config('./config.yaml')

    st = time.time()

    # get dict of id:{filename:encoded_img}
    files = get_images(config)

    rt = time.time()
    read_time = rt - st
    print('Read time:', read_time, 'seconds')

    # send POST request
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    payload = json.dumps(files)
    response = requests.post(config['url'], data=payload, headers=headers)

    # get timings
    et = time.time()
    elapsed_time = et - st
    server_time = et - rt
    print('Server time:', server_time, 'seconds')
    print('Execution time:', elapsed_time, 'seconds')

    # save to file as example
    with open('./data.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
