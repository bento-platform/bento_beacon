from collections import Counter, defaultdict
from copy import deepcopy


def flatten(nested_list):
    return [item for nested_items in nested_list for item in nested_items]


def get_union_of_filtering_terms(filters_dict):
    # create an entry for each filter
    union_filters = []
    for f in filters_dict.values():
        filter = deepcopy(f[0])  # arbitrarily get name, description, etc from first entry
        filter["values"] = values_union([entry["values"] for entry in f])
        union_filters.append(filter)

    return union_filters


def get_intersection_of_filtering_terms(filters_dict, num_beacons_in_network):
    # remove any fields not in all entries
    intersection_dict = {id: entries for id, entries in filters_dict.items() if len(entries) == num_beacons_in_network}

    # create one entry for each id
    intersection_filters = []
    for f in intersection_dict.values():
        filter = deepcopy(f[0])  # arbitrarily get name, description, etc from first entry
        values = values_intersection([entry["values"] for entry in f])
        if values:
            filter["values"] = values
            intersection_filters.append(filter)

    return intersection_filters


def get_filters_dict(filters_list):
    # make a dict of entries, keyed to bento query id, keeping duplicates in an array
    # TODO next version: change key to model mapping (phenopackets / experiments path) instead of bento id
    filters_by_id = defaultdict(list)
    for f in filters_list:
        filter_id = f["id"]
        filters_by_id[filter_id].append(f)
    return filters_by_id


def values_union(options_list):
    # remove duplicates but keep any ordering
    return list(dict.fromkeys(flatten(options_list[:])))


def values_intersection(options_list):
    num_instances = len(options_list)
    flat_options = flatten(options_list[:])

    # only keep options that are present in all instances, preserving order
    counter = Counter(flat_options)
    intersection = [key for key in counter if counter[key] == num_instances]
    return intersection
