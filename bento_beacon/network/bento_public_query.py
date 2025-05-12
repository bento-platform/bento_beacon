import copy

# TEMP FILE
#
# handling for bento public query terms, currently how beacon UI handles search options to present to the user
# to be replaced by beacon spec filtering_terms in a future version
# best approach here is not yet clear:
# - intersection of all query terms is too small
# - union of all query terms loses any organization into categories, which varies across instances
#
# we may prefer to make network query terms configurable rather than generating them automatically


def flatten(nested_list):
    return [item for nested_items in nested_list for item in nested_items]


# don't stringify fields that are explicitly set to null / None
def field_string(field: dict, key: str) -> str:
    value = field.get(key)
    return "__" + value if value is not None else ""


def fields_dict(search_fields):
    """
    Given a list of bento_public search fields, one for each instance,
    return a dictionary of search fields keyed to phenopackets mapping, with an array of all fields for that mapping
    """
    # create a single array of all search fields for all instances, removing nesting
    copy = search_fields[:]

    all_fields = []
    for sf in copy:
        for f in sf:
            all_fields.extend(f["fields"])

    # make a dict of entries, keyed to phenopackets mapping + group_by, etc, keeping duplicate values
    all_fields_by_mapping = {}
    for f in all_fields:
        field_key = (
            f["mapping"]
            + field_string(f, "group_by")
            + field_string(f, "group_by_value")
            + field_string(f, "value_mapping")
        )
        all_fields_by_mapping[field_key] = all_fields_by_mapping.get(field_key, []) + [f]

    return all_fields_by_mapping


def options_union(options_list):
    # remove duplicates but keep any ordering
    return list(dict.fromkeys(flatten(options_list[:])))


def options_intersection(options_list):
    num_instances = len(options_list)
    flat_options = flatten(options_list[:])
    # only keep options that are present in all instances, preserving order
    counter = {}
    for option in flat_options:
        counter[option] = counter.get(option, 0) + 1

    intersection = [key for key in counter if counter[key] == num_instances]
    return intersection


# any filters that exist in all beacons
# bins should be joined also, although some ordering may disappear
# still unclear if this is an useful feature or not
# shortcomings here can be addressed by keeping our configs consistent where possible
def fields_union(search_fields):
    fields = fields_dict(search_fields)

    # create one entry for each mapping
    union_fields = []
    for f in fields.values():
        entry = copy.deepcopy(f[0])  # arbitrarily get name, description, etc from first entry
        entry["options"] = options_union([e["options"] for e in f])
        union_fields.append(entry)

    return union_fields


def fields_intersection(search_fields):
    num_instances = len(search_fields)
    fields = fields_dict(search_fields)

    # remove any fields not in all entries
    intersection_dict = {mapping: entries for mapping, entries in fields.items() if len(entries) == num_instances}

    # create one entry for each mapping
    intersection_fields = []
    for f in intersection_dict.values():
        entry = {}
        entry = copy.deepcopy(f[0])  # arbitrarily get name, description, etc from first entry
        options = options_intersection([e["options"] for e in f])
        if options:
            entry["options"] = options
            intersection_fields.append(entry)

    return intersection_fields
