from utils import download_image, printProgressBar, load_json, save_json
import os
import sys
import multiprocessing as mp
from scraper import PartDetails

py_file = sys.argv[0].split('/')[-1]
base_path = sys.argv[0].replace(py_file, '')

if not os.path.exists(base_path + 'images/'):
    os.mkdir(base_path + 'images/')

if not os.path.exists(base_path + 'images/logs'):
    os.mkdir(base_path + 'images/logs')


# meta_data_list = load_json(base_path + 'images.json')

# for item in meta_data_list:
#     item['path'] = base_path + 'images/'
# total_data_count = len(meta_data_list)


def prepare_image_data():
    meta_file_data = []
    with os.scandir('output/parts') as it:
        for entry in it:
            if entry.name.endswith('.json'):
                part_file = load_json(entry.path)
                for index, image in enumerate(part_file['images']):
                    meta_file_data.append({
                        'url': image,
                        'file_name': entry.name.replace('.json', '') + ' - ' + str(index + 1)
                    })
    save_json(meta_file_data, 'images.json')


def download_image_file(meta):
    download_image(meta)

    path, dirs, files = next(os.walk(base_path + 'images/logs'))
    file_count = len(files)

    printProgressBar(file_count, 14653, prefix='Progress:', suffix='Complete', decimals=2, length=50)


def fetch_image_and_download(part_number):
    log_file_name = base_path + 'images/logs/' + part_number.replace('/', '#').replace('|', '#')
    if os.path.exists(log_file_name):
        return

    scraper = PartDetails()
    image_list = scraper.fetch_images(part_number)

    for index, image in enumerate(image_list):
        download_image_file({
            'path': base_path + 'images/',
            'file_name': part_number.replace('/', '#').replace('|', '#') + ' (' + str(index + 1) + ')',
            'url': image
        })

    with open(log_file_name, 'w') as f:
        f.write('')


if __name__ == '__main__':
    # prepare_image_data()
    # exit(0)

    # mp.freeze_support()



    # print('===', total_data_count, '===')
    # print('Exporting to path', base_path)
    # pool = mp.Pool(50)
    # pool.map(download_image_file, meta_data_list)

    data_file = load_json(base_path + 'images.json')
    pool = mp.Pool(32)
    pool.map(fetch_image_and_download, data_file)

