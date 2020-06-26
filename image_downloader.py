from utils import download_image, printProgressBar, load_json, save_json
import os
import sys
import multiprocessing as mp

py_file = sys.argv[0].split('/')[-1]
base_path = sys.argv[0].replace(py_file, '')

if not os.path.exists(base_path + 'images/'):
    os.mkdir(base_path + 'images/')

meta_data_list = load_json(base_path + 'images.json')

for item in meta_data_list:
    item['path'] = base_path + 'images/'
total_data_count = len(meta_data_list)


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

    path, dirs, files = next(os.walk(base_path + 'images'))
    file_count = len(files)

    printProgressBar(file_count, total_data_count, prefix='Progress:', suffix='Complete', length=50)


if __name__ == '__main__':
    # prepare_image_data()
    # exit(0)

    # mp.freeze_support()

    print('===', total_data_count, '===')
    print('Exporting to path', base_path)
    pool = mp.Pool(50)
    pool.map(download_image_file, meta_data_list)

