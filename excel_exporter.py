import xlsxwriter
import os
from functools import reduce
from utils import load_json, safe_list_index, make_dir, save_json
from multiprocessing import Pool

base_path = 'output/excel/'
make_dir(base_path)
make_dir('output/parts/competitors_merged')


def extract_make_list():
    make_list = []
    with os.scandir('output/data') as it:
        for year_entry in it:
            if os.path.isdir(year_entry.path):
                with os.scandir(year_entry.path) as it2:
                    for make_entry in it2:
                        if os.path.isdir(make_entry.path):
                            make_list.append(make_entry.name)

    make_list = list(dict.fromkeys(make_list))
    return make_list


def load_part_details(part_number):
    file_name = 'output/parts/' + part_number + '.json'
    if os.path.exists(file_name):
        return load_json(file_name)
    else:
        print('File not found', part_number)
        return None


def load_competitors(part_number):
    file_name = 'output/parts/competitors_merged/' + part_number + '.json'
    if os.path.exists(file_name):
        data_file = load_json(file_name)
        return reduce(lambda x, y: x + 'POP: ' + y['pop'] + '|'
                                   + 'Per Car: ' + str(y['qtyEach']) + '|'
                                   + 'COMP/OE #: ' + y['mfG_Part'] + '|'
                                   + 'COMP/OE: ' + y['mfg'] + '^',
                      data_file, '')
    else:
        print('File not found', part_number)
        return ''


def export(for_make):
    print(for_make)
    workbook = xlsxwriter.Workbook(base_path + for_make + '.xlsx', {'strings_to_urls': False})
    worksheet = workbook.add_worksheet('Four Seasons')

    if os.path.exists(base_path + for_make + '.xlsx'):
        return

    worksheet.write('A1', 'Year')
    worksheet.write('B1', 'Make')
    worksheet.write('C1', 'Model')
    worksheet.write('D1', 'Engine')
    worksheet.write('E1', 'Category')
    worksheet.write('F1', 'Part Number')
    worksheet.write('G1', 'Part Name')
    worksheet.write('H1', 'Competitors')
    worksheet.write('I1', 'Part Specifications')
    worksheet.write('J1', 'Description')
    worksheet.write('K1', 'Buyers Guide')
    worksheet.write('L1', 'image Url')
    worksheet.write('M1', '')
    worksheet.write('N1', '')
    worksheet.write('O1', '')
    worksheet.write('P1', '')
    worksheet.write('Q1', "")
    worksheet.write('R1', '')
    worksheet.write('S1', '')
    worksheet.write('T1', '')
    worksheet.write('U1', '')
    worksheet.write('V1', '')
    worksheet.write('W1', '')
    worksheet.write('X1', '')
    worksheet.write('Y1', '')
    worksheet.write('Z1', '')

    worksheet.set_column('A:C', 10)
    worksheet.set_column('D:F', 20)
    worksheet.set_column('G:K', 30)

    row, col = 1, 0
    with os.scandir('output/data') as it:
        for year_entry in it:
            if os.path.isdir(year_entry.path):
                with os.scandir(year_entry.path) as it2:
                    for make_entry in it2:
                        if os.path.isdir(make_entry.path) and for_make == make_entry.name:
                            with os.scandir(make_entry.path) as it3:
                                for model_entry in it3:
                                    if model_entry.name.endswith('.json'):
                                        data_file = load_json(model_entry.path)
                                        for part_item in data_file:
                                            part_details = load_part_details(part_item['basePart'])
                                            competitors = load_competitors(part_item['basePart'])
                                            if part_details is None:
                                                continue

                                            worksheet.write(row, col, year_entry.name)
                                            worksheet.write(row, col + 1, make_entry.name.replace('|', '/'))
                                            worksheet.write(row, col + 2,
                                                            model_entry.name.replace('|', '/').replace('.json', ''))
                                            worksheet.write(row, col + 3, part_item['engine']['engine'])
                                            worksheet.write(row, col + 4, part_item['categoryName_en'])
                                            worksheet.write(row, col + 5, part_item['basePart'])
                                            worksheet.write(row, col + 6, part_item['partDesc_en'])

                                            worksheet.write(row, col + 7, competitors)
                                            specifications = reduce(
                                                lambda x, y: x + y['attributeName_en'] + '|' + y['siteValue_en'] + '^',
                                                part_details['partSpecs'], '')
                                            worksheet.write(row, col + 8, specifications)

                                            description = reduce(
                                                lambda x, y: x + y['fbDesc'] + '^',
                                                part_details['fandB'], '')

                                            worksheet.write(row, col + 9, description)

                                            buyers_guide = reduce(lambda x, y: x + y['buyersGuideDesc'] + '^',
                                                                  part_details['buyersGuides'], '')
                                            worksheet.write(row, col + 10, buyers_guide)

                                            for index, image in enumerate(part_details['images']):
                                                worksheet.write(row, col + 11 + index, image)

                                            print('\r',for_make, row, end='')
                                            row += 1

                                            # if row > 1000:
                                            #     workbook.close()
                                            #     exit(0)

    workbook.close()
    print()
    # exit(0)


def prepare_competitor_data(part_number):
    output_data = []
    output_path = 'output/parts/competitors_merged/' + part_number + '.json'

    with os.scandir('output/parts/competitors') as it:
        for index, entry in enumerate(it):
            # print('\r', index, end='')

            if entry.name.endswith('.json'):
                search_result_file = load_json(entry.path)
                for item in search_result_file:
                    if item['basePart'] == part_number:

                        item_already_exists = False
                        for output_item in output_data:
                            if output_item['mfg'] == item['mfg'] and output_item['mfG_Part'] == item['mfG_Part']:
                                item_already_exists = True
                                break
                        if item_already_exists:
                            continue
                        output_data.append(item)
    save_json(output_data, output_path)

    _, _, f = next(os.walk('output/parts/competitors_merged'))
    print('\r', len(f), end='')


def export_competitor_data():
    workbook = xlsxwriter.Workbook(base_path + 'competitors' + '.xlsx', {'strings_to_urls': False})
    worksheet = workbook.add_worksheet('Four Seasons')

    worksheet.write('A1', 'Part Number')
    worksheet.write('B1', 'Part Name')
    worksheet.write('C1', 'POP')
    worksheet.write('D1', 'Per Car')
    worksheet.write('E1', 'COMP/OE Number')
    worksheet.write('F1', 'COMP/OE Name')

    worksheet.set_column('A:F', 20)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:D', 10)

    row, col = 1, 0

    with os.scandir('output/parts/competitors_merged') as it:
        for entry in it:
            if entry.name.endswith('.json'):
                data_file = load_json(entry.path)
                for item in data_file:
                    worksheet.write(row, col, item['basePart'])
                    worksheet.write(row, col + 1, item['partDesc_en'])
                    worksheet.write(row, col + 2, item['pop'])
                    worksheet.write(row, col + 3, item['qtyEach'])
                    worksheet.write(row, col + 4, item['mfG_Part'])
                    worksheet.write(row, col + 5, item['mfg'])

                    print('\r', row, end='')
                    row += 1

    workbook.close()


if __name__ == '__main__':
    make_list = extract_make_list()
    # export('Acura')

    pool = Pool(10)
    pool.map(export, make_list)

    # for item in make_list:
    #     export(item)

    # part_list = []
    #
    # with os.scandir('output/parts') as it:
    #     for entry in it:
    #         if entry.name.endswith('.json'):
    #             part_number = entry.name.replace('.json', '')
    #             output_path = 'output/parts/competitors_merged/' + part_number + '.json'
    #             if os.path.exists(output_path):
    #                 continue
    #             part_list.append(part_number)
    #
    # pool = Pool(50)
    # pool.map(prepare_competitor_data, part_list)

    # export_competitor_data()
