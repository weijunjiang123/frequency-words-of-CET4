import re
import json

def select_url_list():
    with open('./link_list.txt', 'r', encoding='utf-8') as f :
        link_list = json.load(f)
    new_link_list = list(filter(lambda x: re.match('^\d.*?选词填空$?', x[0]) != None, link_list))
    # new_link_list = []
    # for data in link_list:
    #     if re.match('^\d.*?选词填空$', data[0]) != None:
    #         new_link_list.append(data)
    #         print(data)
    print(new_link_list)
    
    
select_url_list()