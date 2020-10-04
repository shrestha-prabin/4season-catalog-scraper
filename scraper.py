import requests
from functools import reduce
import re
import os
from utils import save_json, load_json, make_dir, file_counter
from time import sleep
import json
from multiprocessing import Pool

base_url = 'https://ecatalog.smpcorp.com/V2/FS/api/'


class PartList:

    def extract_part_list(self, for_year=None):
        year_list = self.fetch_year_list()
        for year_item in year_list:
            print(year_item)
            if for_year is not None and year_item != for_year:
                continue
            make_dir('output/data/' + year_item)
            make_list = self.fetch_make_list(year_item)
            for make_item in make_list:
                print(year_item, make_item)
                make_dir('output/data/' + year_item + '/' + make_item.replace('/', '|'))
                model_list = self.fetch_model_list(year_item, make_item)

                for model_item in model_list:
                    print(year_item, make_item, model_item)
                    part_list_for_model = []
                    output_file_path = 'output/data/' + year_item + '/' + make_item.replace('/',
                                                                                            '|') + '/' + model_item.replace(
                        '/', '|') + '.json'
                    if os.path.exists(output_file_path):
                        continue

                    engine_list = self.fetch_engine_list(year_item, make_item, model_item)
                    for engine_item in engine_list:
                        parts_list = self.fetch_parts_list(year_item, make_item, model_item, engine_item)
                        part_list_for_model.extend(parts_list)

                    save_json(part_list_for_model, output_file_path)

    def fetch_year_list(self):
        response = requests.get(base_url + 'vehicle/years')
        response = json.loads(response.text)
        year_list = []
        for item in response:
            year_list.append(item['year'])
        return year_list

    def fetch_make_list(self, year):
        response = requests.get(base_url + 'vehicle/makes?year=' + year)
        response = json.loads(response.text)
        make_list = []
        for item in response:
            make_list.append(item['make'])
        return make_list

    def fetch_model_list(self, year, make):
        response = requests.get(base_url + 'vehicle/models?year=' + year + '&make=' + make)
        response = json.loads(response.text)
        model_list = []
        for item in response:
            model_list.append(item['model'])
        return model_list

    def fetch_engine_list(self, year, make, model):
        response = requests.get(base_url + 'vehicle/engines?year=' + year + '&make=' + make + '&model=' + model)
        response = json.loads(response.text)
        engine_list = response
        return engine_list

    def fetch_parts_list(self, year, make, model, engine):
        response = requests.get(base_url
                                + 'part/partsearch'
                                  '?filter=ymme'
                                  '&filterType=n'
                                  '&searchType=p'
                                  '&imageSize=80'
                                  '&start=0'
                                  '&limit=1000000'
                                  '&sort=1'
                                  '&catFilter=-All-'
                                  '&yearFilter=' + year
                                + '&makeFilter=' + make
                                + '&modelFilter=' + model
                                + '&engineFilter=' + engine['engine']
                                + '&attrCodeFilter=-All-'
                                  '&attrValueFilter=-All-'
                                )
        response = json.loads(response.text)
        for item in response:
            item['engine'] = engine
        return response


class PartDetails:

    def extract_part_details(self):
        # Get Available Parts List
        part_meta_list = []
        with os.scandir('output/data') as it1:
            for year_entry in it1:
                if os.path.isdir(year_entry.path):
                    with os.scandir(year_entry.path) as it2:
                        for make_entry in it2:
                            if os.path.isdir(make_entry):
                                print('\r', year_entry.name, make_entry.name, end='')
                                with os.scandir(make_entry.path) as it3:
                                    for model_entry in it3:
                                        if model_entry.name.endswith('.json'):
                                            data_file = load_json(model_entry.path)
                                            for part_item in data_file:
                                                part_number = part_item['basePart']
                                                file_name = 'output/parts/' + part_number + '.json'
                                                if not os.path.exists(file_name):
                                                    part_meta_list.append({
                                                        'part_number': part_number,
                                                        'category': part_item['categoryName_en']
                                                    })
        print()

        # Remove Duplicates
        temp = []
        for part_item in part_meta_list:
            item_exists = False
            for item in temp:
                if item['part_number'] == part_item['part_number']:
                    item_exists = True
                    break
            if not item_exists:
                temp.append(part_item)
        part_meta_list = temp

        print('===', len(part_meta_list), '===')

        pool = Pool(24)
        pool.map(self.fetch_and_export_part_details, part_meta_list)

    def fetch_and_export_part_details(self, meta):
        part_number = meta['part_number']
        output_file_name = 'output/parts/' + part_number + '.json'

        part_details = self.fetch_part_details(part_number)
        part_details['category'] = meta['category']
        part_details['images'] = self.fetch_images(part_number)

        save_json(part_details, output_file_name)
        # print(part_number)
        print('\r', file_counter('output/parts'), end='')

    def fetch_part_details(self, part_number):
        print('\r.', end='')
        response = requests.get(base_url
                                + 'part/partselect'
                                  '?part=' + part_number
                                + '&func=PART'
                                  '&vid=303910')
        response = json.loads(response.text)
        return response['pp']

    def fetch_images(self, part_number):
        # print('\r..', end='')
        response = requests.get(base_url
                                + 'image/getallimages'
                                  '?partNum=' + part_number
                                + '&brand=FS'
                                  '&zoomFactor_sm=75'
                                  '&zoomFactor_md=360'
                                  '&zoomFactor_bg=960')
        response = json.loads(response.text)

        image_list = []
        for image_item in response:
            image_list.append(image_item['image_BG_Url'])
        return image_list

    def extract_competitor_oe(self):
        make_dir('output/parts/search_query')
        make_dir('output/parts/competitors')
        query_list = []
        for search_query in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                             's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            query_list.append(search_query)

        pool = Pool(4)
        # pool.map(self.fetch_and_save_search_query, query_list)
        # pool.map(self.fetch_and_save_competitor_oe, query_list)
        self.fetch_and_save_competitor_oe('n')


    def fetch_and_save_search_query(self, search_query):
        output_file = 'output/parts/search_query/' + search_query + '.json'
        if os.path.exists(output_file):
            return

        response = requests.get('https://ecatalog.smpcorp.com/V2/FS/api/Vehicle/autosearch'
                                '?func=PART'
                                '&filter=' + search_query +
                                '&count=100000000'
                                '&searchType=X'
                                '&site=FS')
        response = json.loads(response.text)
        print(search_query, ':', len(response))
        save_json(response, output_file)


    def extract_competitor_details(self):
        search_query_3 = []
        with os.scandir('output/parts/search_query') as it:
            for entry in it:
                if entry.name.endswith('.json'):
                    data_file = load_json(entry.path)
                    for item in data_file:
                        query = item.split(' - ')[0][0:3]
                        search_query_3.append(query)
                        print('\r', entry.name, end='')

        search_query_3 = list(dict.fromkeys(search_query_3))
        print(len(search_query_3))
        save_json(search_query_3, 'output/parts/search_query/_sub_3.json')

        # search_query_3 = load_json('output/parts/search_query/_sub_3.json')


    def fetch_and_save_competitor_oe(self, search_query):
        output_file = 'output/parts/competitors/' + search_query + '.json'
        if os.path.exists(output_file):
            return

        print('Search', search_query)
        response = requests.get(base_url
                                + 'part/partsearch'
                                  '?filter=' + search_query + '  '
                                + '&filterType=s'
                                  '&searchType=x'
                                  '&imageSize=80'
                                  '&start=0'
                                  '&limit=10000000'
                                  '&sort=1'
                                  '&catFilter=-All-'
                                  '&yearFilter=-All-'
                                  '&makeFilter=-All-'
                                  '&modelFilter=-All-'
                                  '&engineFilter=-All-'
                                  '&attrCodeFilter=-All-'
                                  '&attrValueFilter=-All-')
        response = json.loads(response.text)
        print(search_query, ':', len(response))
        for item in response:
            item.pop('brand')
            item.pop('brandLink')
            item.pop('maxRows')
            item.pop('partComment')
            item.pop('rowId')
            item.pop('categoryName_en')
            item.pop('imageUrl')
            item.pop('vehicleId')
            item.pop('site')
            item.pop('webBase')
            item.pop('webColumn_Id')
        save_json(response, output_file)

