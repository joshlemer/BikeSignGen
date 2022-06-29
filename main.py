import xml.etree.ElementTree as ET
import csv

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
    has_icons = len(destination['icons']) != 0
    name_id_no_icons, name_id_with_icons = (f'''Destination{position}.{'WithIcons.' if with_icons else ''}Name''' for with_icons in (False, True))

    shown_name_id, hidden_name_id = name_id_no_icons, name_id_with_icons 
    if has_icons:
        shown_name_id, hidden_name_id = hidden_name_id, shown_name_id 

    shown_name_elem: ET.Element = find_elem_by_id(root, shown_name_id)
    hidden_name_elem: ET.Element = find_elem_by_id(root, hidden_name_id)

    set_hidden(shown_name_elem, is_hidden=False)
    set_hidden(hidden_name_elem, is_hidden=True)

    set_text(shown_name_elem, destination['name'])

    for icon in ('Dining', 'Grocery', 'Skytrain', 'Washroom'):
        set_hidden(find_elem_by_id(root, f'Destination{position}.Icon.{icon}'), icon not in destination['icons'])
    
    for direction in ('Left', 'Right', 'Up'):
        set_hidden(find_elem_by_id(root, f'Destination{position}.Direction.{direction}'), direction != destination['direction'])

    set_text(find_elem_by_id(root, f'Destination{position}.Distance'), destination['distance'])
    set_text(find_elem_by_id(root, f'Destination{position}.TravelTime'), destination['travelTime'])
    set_text(find_elem_by_id(root, f'Destination{position}.ElevationGain'), destination['elevationGain'])

    for comfort in ('Circle', 'Square', 'Diamond'):
        set_hidden(find_elem_by_id(root, f'Destination{position}.Comfort.{comfort}'), comfort != destination['comfort'])


## Returns iterable of dicts 
def parse_csv(file_name):
    '''
    returns iterable of dicts like 
    {
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

        def copy_if_not_empty(from_dict, to_dict, field):
            value = from_dict[field]
            if value:
                to_dict[field] = value
        
        result = {}

        for field in ('name', 'distance', 'travelTime', 'elevationGain', 'direction', 'comfort'):
            copy_if_not_empty(row, result, field)
        

        


        return row
    with open(file_name,newline='') as csvfile:
        return [row for row in csv.DictReader(csvfile)]
 


# def main():
#     template_path = 'templates/trifold_landscape.svg'

#     root = ET.parse(template_path)

#     apply_destination(root, destination0, 0)
#     apply_destination(root, destination1, 1)
#     apply_destination(root, destination2, 2)

#     root.write('out/testing.svg')


main()



def test():

    root = ET.parse(template_path)
    find_elem_by_id(root, 'Destination0.WithIcons.Name')
    find_elem_by_id(root, 'Destination0.Icon.Dining')

    e = root.find('.//*[@id="Destination0.Icon.Dining"]')

    id = 'Destination0.Icon.Dining'
    p = f""".//*[@id="{id}"]"""
    root.find(p)


    return 

