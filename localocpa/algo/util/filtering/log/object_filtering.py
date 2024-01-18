from localocpa.objects.log.util import misc as log_util


def filter_sublog_objects(ocel, objects):
    '''
    Filters process executions from an ocel

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param objects: list of objects to be included (in form tuple (ot, o))
    :type threshold: list(int)

    :return: Object-centric event log
    :rtype: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    '''


    new_event_df = ocel.log.log.copy()
    new_event_df["event_objects"] = new_event_df.apply(
        lambda x: [(ot, o) for ot in ocel.object_types for o in x[ot]], axis=1)
    new_event_df["event_objects"] = new_event_df["event_objects"].apply(lambda x: list(set(x).intersection(set(objects))))
    new_event_df["contains_objects"] = new_event_df["event_objects"].apply(lambda x: True if x != [] else False)
    new_event_df = new_event_df[new_event_df["contains_objects"]]

    #remove unused object references
    new_event_df["event_objects"] = new_event_df["event_objects"].apply(lambda x: list(set(x).intersection(set(objects))))
    for ot in ocel.object_types:
        new_event_df[ot] = new_event_df["event_objects"].apply(
            lambda x: [o for (ot_, o) in x if ot_ == ot])
    new_event_df.drop('event_objects', axis=1, inplace=True)
    new_event_df.drop('contains_objects', axis=1, inplace=True)
    new_log = log_util.copy_log_from_df(new_event_df, ocel.parameters)
    return new_log