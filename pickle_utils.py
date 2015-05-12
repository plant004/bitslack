# -*- coding: utf-8 -*-
import pickle

def load(file_path, default={}):
    result = default
    try:
        fp = open(file_path, 'r')
        result = pickle.load(fp)
        fp.close()
    except Exception, e:
        print e
        result = default
    return result

def save(dict_data, file_path):
    try:
        fp = open(file_path, 'w')
        pickle.dump(dict_data, fp)
        fp.close()
    except Exception, e:
        pass
