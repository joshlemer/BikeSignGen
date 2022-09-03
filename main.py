import os
import re
import xml.etree.ElementTree as ET
import csv
import itertools
import yaml
from jinja2 import Environment, PackageLoader, select_autoescape

# import pdfkit
# from weasyprint import HTML
from pyppeteer import launch
import asyncio
destinations = [{
    'name': "Josh's",
    'distance': 7.6,
    'travelTime': 23,
    'elevationGain': 3,
    'direction': 'left',
    'icons': {'dining', 'skytrain', 'washroom'},
}]
destination0 = {
    'name': "Josh's",
    'distance': '1.1km',
    'travelTime': '2min',
    'elevationGain': '3m',
    'direction': 'Left',
    'icons': {'Dining', 'Skytrain', 'Washroom'},
    'comfort': 'Square',
}
destination1 = {
    'name': "Shivs's",
    'distance': '4.4km',
    'travelTime': '5min',
    'elevationGain': '6m',
    'direction': 'Right',
    'icons': {},
    'comfort': 'Diamond',
}
destination2 = {
    'name': "Tyler's",
    'distance': '7.7km',
    'travelTime': '8min',
    'elevationGain': '9m',
    'direction': 'Up',
    'icons': {'Skytrain'},
    'comfort': 'Circle',
}

def find_elem_by_id(root, id):
    path = f""".//*[@id="{id}"]"""
    result = root.find(path)
    if result == None:
        raise Exception(f'No element with id {id}, at path "{path}"')
    return result 

def set_hidden(elem: ET.Element, is_hidden):
    if is_hidden:
        elem.attrib['style'] = 'display:none;'
    elif 'style' in elem.attrib:
        elem.attrib['style'] = elem.attrib['style'].replace('display:none', '')
            

def set_text(elem: ET.Element, text):
    elem[0].text = text

def apply_destination(root, destination, position):
    print(destination)
    has_icons = 'icons' in destination and len(destination['icons']) != 0
    name_id_no_icons, name_id_with_icons = (f'''Destination{position}.{'WithIcons.' if with_icons else ''}Name''' for with_icons in (False, True))

    shown_name_id, hidden_name_id = name_id_no_icons, name_id_with_icons 
    if has_icons:
        shown_name_id, hidden_name_id = hidden_name_id, shown_name_id 

    shown_name_elem: ET.Element = find_elem_by_id(root, shown_name_id)
    hidden_name_elem: ET.Element = find_elem_by_id(root, hidden_name_id)

    if 'name' in destination:
        set_hidden(shown_name_elem, is_hidden=False)
        set_text(shown_name_elem, destination['name'])
    else:
        set_hidden(shown_name_elem, is_hidden=True)

    set_hidden(hidden_name_elem, is_hidden=True)

    for icon in ('Dining', 'Grocery', 'Skytrain', 'Washroom'):
        set_hidden(find_elem_by_id(root, f'Destination{position}.Icon.{icon}'), 'icons' not in destination or icon.lower() not in destination['icons'])
    
    for direction in ('Left', 'Right', 'Up'):
        set_hidden(find_elem_by_id(root, f'Destination{position}.Direction.{direction}'), 'direction' not in destination or direction.lower() != destination['direction'].lower())

    if 'distance' in destination:
        set_text(find_elem_by_id(root, f'Destination{position}.Distance'), destination['distance'])
    else:
        set_hidden(find_elem_by_id(root, f'Destination{position}.Distance'), True)

    if 'travelTime' in destination:
        set_text(find_elem_by_id(root, f'Destination{position}.TravelTime'), destination['travelTime'])
    else:
        set_hidden(find_elem_by_id(root, f'Destination{position}.Icon.TravelTime'), True)
        set_hidden(find_elem_by_id(root, f'Destination{position}.TravelTime'), True)
    
    if 'elevationGain' in destination:
        set_text(find_elem_by_id(root, f'Destination{position}.ElevationGain'), destination['elevationGain'])
    else:
        set_hidden(find_elem_by_id(root, f'Destination{position}.Icon.ElevationGain'), True)
        set_hidden(find_elem_by_id(root, f'Destination{position}.ElevationGain'), True)

    for comfort in ('Circle', 'Square', 'Diamond'):
        set_hidden(find_elem_by_id(root, f'Destination{position}.Comfort.{comfort}'), 'comfort' not in destination or comfort.lower() != destination['comfort'].lower())


def flatten_yaml(y) -> list(dict()):
    result = []
    for signLocation in y['signLocations']:
        for destination_id, destination in signLocation['destinations'].items():
            location_destination_attribs = y['destinations'][destination_id]
            dest = {
                'location': signLocation['name'],
                'name': location_destination_attribs['name'],

                'direction': destination['direction'],
                'icons': set(location_destination_attribs['amenities']),
            }


            for key in ('distance', 'travelTime', 'elevationGain', 'comfort'):
                if value := destination.get(key):
                    dest[key] = value
            
            result.append(dest)
            print('hi')
    return result


## Returns iterable of dicts 
def parse_csv(file_name):
    '''
    returns iterable of dicts like 
    {
        'location': 'Goring Eastbound at Holdom',
        'name': "Tyler's",
        'distance': '7.7km',
        'travelTime': '8min',
        'elevationGain': '9m',
        'direction': 'Up',
        'icons': {'Skytrain'},
        'comfort': 'Circle',
    }
    '''

    def parse_row(row):

        def copy_if_not_empty(from_dict, from_field, to_dict, to_field):
            value = from_dict[from_field]
            if value:
                to_dict[to_field] = value
        
        result = {}

        for from_field, to_field in {
            'Sign Location Name':'location',
            'Destination Name': 'name', 
            'Distance': 'distance', 
            'Travel Time': 'travelTime', 
            'Elevation Gain': 'elevationGain', 
            'Comfort': 'comfort',
            }.items():
            copy_if_not_empty(row, from_field, result, to_field)
        
        if 'Direction' in row:
            if direction := row['Direction'].strip():
                result['direction'] = f'{direction[0].upper()}{direction[1:]}'
            
            
        
        icons = set()
        for field, icon in {
            'Has Dining': 'dining',
            'Has Grocery': 'grocery',
            'Has Skytrain': 'skytrain',
            'Has Washroom': 'washroom',
            }.items():
            if field in row and row[field]:
                icons.add(icon)

        result['icons'] = icons
        return result 

    with open(file_name,newline='') as csvfile:
        return [parse_row(row) for row in csv.DictReader(csvfile)]

# def parse_yaml(file_name):
#     '''
#     returns iterable of dicts like 
#     {
#         'name': "Tyler's",
#         'distance': '7.7km',
#         'travelTime': '8min',
#         'elevationGain': '9m',
#         'direction': 'Up',
#         'icons': {'Skytrain'},
#         'comfort': 'Circle',
#     }
#     '''

#     def parse_row(row):

#         def copy_if_not_empty(from_dict, from_field, to_dict, to_field):
#             value = from_dict[from_field]
#             if value:
#                 to_dict[to_field] = value
        
#         result = {}

#         for from_field, to_field in {
#             'Sign Location Name':'location',
#             'Destination Name': 'name', 
#             'Distance': 'distance', 
#             'Travel Time': 'travelTime', 
#             'Elevation Gain': 'elevationGain', 
#             'Comfort': 'comfort',
#             }.items():
#             copy_if_not_empty(row, from_field, result, to_field)
        
#         if 'Direction' in row:
#             if direction := row['Direction'].strip():
#                 result['direction'] = f'{direction[0].upper()}{direction[1:]}'
            
            
        
#         icons = set()
#         for field, icon in {
#             'Has Dining': 'Dining',
#             'Has Grocery': 'Grocery',
#             'Has Skytrain': 'Skytrain',
#             'Has Washroom': 'Washroom',
#             }.items():
#             if field in row and row[field]:
#                 icons.add(icon)

#         result['icons'] = icons
#         return result 

#     with open(file_name,newline='') as csvfile:
#         return [parse_row(row) for row in csv.DictReader(csvfile)]


# def main():
#     template_path = 'templates/trifold_landscape.svg'

#     root = ET.parse(template_path)

#     apply_destination(root, destination0, 0)
#     apply_destination(root, destination1, 1)
#     apply_destination(root, destination2, 2)

#     root.write('out/testing.svg')

# main()

max_destinations_per_sign = 6

distance_re = re.compile('(\d+(\.\d+)?)')

def compute_distance(destination) -> float:
    if 'distance' not in destination:
        return 0.0
    matches = distance_re.findall(destination['distance'])
    if len(matches) == 0:
        return 0.0
    
    return float(matches[0][0])

direction_to_num = {'': 0, 'up': 1, 'left': 2, 'right': 3}

def compare_destination(destination):
    direction = destination.get('direction', '')
    return (direction_to_num[direction], compute_distance(destination))




def main2():
    out_dir = os.path.join('out','test2')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    with open('data/burnaby.yml', 'r') as f:
        y = yaml.full_load(f)
        print(y['destinations'])
    # csv_data = parse_csv('data/burnaby.yml')
    # locations = [(location, sorted(list(destinations), key=compare_destination)) 
    #                 for location, destinations in itertools.groupby(csv_data, lambda x: x['location'])]

    template_path = 'templates/ledger_portrait_6.svg'

def main():
    out_dir = os.path.join('out','test3')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    csv_data = parse_csv('data/burnaby.csv')

    with open('data/burnaby.yml', 'r') as f:
        flattened_yaml = flatten_yaml(yaml.full_load(f))
    
    locations = [(location, sorted(list(destinations), key=compare_destination)) for location, destinations in itertools.groupby(flattened_yaml, lambda x: x['location'])]

    # template_path = 'templates/ledger_portrait_6.svg'
    template_path = 'ledger_portrait_6.svg'

    for location, destinations in locations:

        destination_groups = []
        for i, destination in enumerate(destinations):
            if i % max_destinations_per_sign == 0:
                destination_groups.append([])
            destination_groups[-1].append(destination)

        for group_num, group in enumerate(destination_groups):
            root = ET.parse(template_path)
            for i in range(max_destinations_per_sign):
                if len(group) > i:
                    apply_destination(root, group[i], i)
                else:
                    apply_destination(root, {}, i)
            
            root.write(os.path.join(out_dir, f"{location.replace(' ', '_')}_{group_num+1}of{len(destination_groups)}.svg"))
        
async def main3():
    env = Environment(
        loader=PackageLoader('main'),
        autoescape=select_autoescape,
    )
    template = env.get_template('test2.html')
    html_str = template.render({
        'foo': 'bar!!',
        'destinations': [1,2,3,4,5],
    })
    # pdfkit.from_string(html_str,'out.pdf', options={
    #     'page-size': 'Tabloid',
    # })
    # main()
    browser = await launch({'headless': True})
    page = await browser.newPage()

    await page.setContent(html_str)
    await page.pdf({
        'path': 'out2.pdf',
        'printBackground': True,
        'format': 'Tabloid',
    })
    # await page.create



if __name__ == '__main__':
     asyncio.get_event_loop().run_until_complete(main3())





# def test():

#     root = ET.parse(template_path)
#     find_elem_by_id(root, 'Destination0.WithIcons.Name')
#     find_elem_by_id(root, 'Destination0.Icon.Dining')

#     e = root.find('.//*[@id="Destination0.Icon.Dining"]')

#     id = 'Destination0.Icon.Dining'
#     p = f""".//*[@id="{id}"]"""
#     root.find(p)



#     with open('data/testing_data.csv',newline='') as csvfile:
#         d = [row for row in csv.DictReader(csvfile)]
    
#     d[0]

#     return 

