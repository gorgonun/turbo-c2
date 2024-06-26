from turbo_c2.helpers.path_mapping import PathMapping


def merge(target: PathMapping, to_merge: PathMapping):
    for key, value in to_merge.get_all_resources():
        target.put_resource(key, value)
    
    return target
