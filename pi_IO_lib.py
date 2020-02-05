
from collections import OrderedDict
import json

def file_to_dict(nameStr, dir=''):
    """
    Sets attributes for the object anObject from the keys and values of dictionay aDict loaded from the file
    :param nameStr: The full file name
    :param dir: Directory of the file
    :return:dictionary of the configs
    """
    try:
        filename = nameStr
        errFlag = False
        with open(dir + filename, 'r') as fp:
            data = fp.read()
            data = data.rstrip("\n")
            data = data.replace('\n', ',')
            data = data.replace('=', ':')
            configDict = json.loads(data)
            print(str(configDict))
            fp.close()
    except FileNotFoundError as e:
        raise e
    return configDict

def dict_to_file(anyDict, nameStr, dir=''):
    """
     Saves a dicitonary as JSON encoded text file
    :param anyDict Dictionary to be converted
    :param nameStr: Name of JSON file
    :param dir: Directory to save JSON file
    :return: None
    """
    configFile = nameStr
    with open(dir + configFile, 'w') as fp:
        fp.write(json.dumps(anyDict, separators=('\n', '='), sort_keys=True, skipkeys=True))
        fp.close()

def show_ordered_dict(objectDict, longName):
    """
    Dumps standard dictionary settings into an ordered dictionary, prints settings to screen in a numbered fashion from the ordered dictionary,
    making it easy to select a setting to change. Returns an  ordered dictionary of {number:(key:value),} used by edit_dict function
    :param longName:
    :return:
    """
    print('\n*************** Current %s Settings *******************' % longName)
    showDict = OrderedDict()
    itemDict = {}
    nP = 0
    for key in sorted(objectDict):
        value = objectDict.get(key)
        print(value)
        showDict.update({nP: {key: value}})
        nP += 1
    for ii in range(0, nP):
        itemDict.update(showDict[ii])
        kvp = itemDict.popitem()
        print(str(ii + 1) + ') ', kvp[0], ' = ', kvp[1])
    print('**********************************\n')
    return showDict
