from turbo_c2.abstractions.job_group import JobGroup
from turbo_c2.abstractions.job_group_with_instances import JobGroupWithInstances
from turbo_c2.domain.gui.layout_definition import (
    ItemPositionDefinition,
    JobInstancePositionDefinition,
    LayoutDefinition,
    QueuePositionDefinition,
    WindowDefinition,
)
from turbo_c2.helpers.name_utils import NameUtils


# Ex:
# {
#     "name": "root",
#     "directed": true,
#     "strict": false,
#     "_draw_": [
#         {
#             "op": "c",
#             "grad": "none",
#             "color": "#fffffe00"
#         },
#         {
#             "op": "C",
#             "grad": "none",
#             "color": "#ffffff"
#         },
#         {
#             "op": "P",
#             "points": [
#                 [
#                     0.0,
#                     0.0
#                 ],
#                 [
#                     0.0,
#                     324.0
#                 ],
#                 [
#                     900.0,
#                     324.0
#                 ],
#                 [
#                     900.0,
#                     0.0
#                 ]
#             ]
#         }
#     ],
#     "bb": "0,0,900,324",
#     "xdotversion": "1.7",
#     "_subgraph_cnt": 0,
#     "objects": [
#         {
#             "_gvid": 0,
#             "name": "JobInstance_2def974750944911b60a9ca4df26d088",
#             "_draw_": [
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "e",
#                     "rect": [
#                         144.0,
#                         252.0,
#                         144.0,
#                         72.0
#                     ]
#                 }
#             ],
#             "_ldraw_": [
#                 {
#                     "op": "F",
#                     "size": 14.0,
#                     "face": "Times-Roman"
#                 },
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "T",
#                     "pt": [
#                         144.0,
#                         248.3
#                     ],
#                     "align": "c",
#                     "width": 70.0,
#                     "text": "consumer"
#                 }
#             ],
#             "height": "2",
#             "label": "consumer",
#             "pos": "144,252",
#             "width": "4"
#         },
#         {
#             "_gvid": 1,
#             "name": "JobInstance_4af6428eb93245a6b5526e532f2f883c",
#             "_draw_": [
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "e",
#                     "rect": [
#                         144.0,
#                         72.0,
#                         144.0,
#                         72.0
#                     ]
#                 }
#             ],
#             "_ldraw_": [
#                 {
#                     "op": "F",
#                     "size": 14.0,
#                     "face": "Times-Roman"
#                 },
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "T",
#                     "pt": [
#                         144.0,
#                         68.3
#                     ],
#                     "align": "c",
#                     "width": 134.0,
#                     "text": "sum_one_producer"
#                 }
#             ],
#             "height": "2",
#             "label": "sum_one_producer",
#             "pos": "144,72",
#             "width": "4"
#         },
#         {
#             "_gvid": 2,
#             "name": "JobInstance_ea70e278f8b743f3acf4acbe333f40ea",
#             "_draw_": [
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "e",
#                     "rect": [
#                         450.0,
#                         252.0,
#                         144.0,
#                         72.0
#                     ]
#                 }
#             ],
#             "_ldraw_": [
#                 {
#                     "op": "F",
#                     "size": 14.0,
#                     "face": "Times-Roman"
#                 },
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "T",
#                     "pt": [
#                         450.0,
#                         248.3
#                     ],
#                     "align": "c",
#                     "width": 59.0,
#                     "text": "sum_job"
#                 }
#             ],
#             "height": "2",
#             "label": "sum_job",
#             "pos": "450,252",
#             "width": "4"
#         },
#         {
#             "_gvid": 3,
#             "name": "JobInstance_bb9edaceb0cd4aba850e5e4589ea8cad",
#             "_draw_": [
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "e",
#                     "rect": [
#                         756.0,
#                         252.0,
#                         144.0,
#                         72.0
#                     ]
#                 }
#             ],
#             "_ldraw_": [
#                 {
#                     "op": "F",
#                     "size": 14.0,
#                     "face": "Times-Roman"
#                 },
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "T",
#                     "pt": [
#                         756.0,
#                         248.3
#                     ],
#                     "align": "c",
#                     "width": 119.0,
#                     "text": "register_handler"
#                 }
#             ],
#             "height": "2",
#             "label": "register_handler",
#             "pos": "756,252",
#             "width": "4"
#         }
#     ],
#     "edges": [
#         {
#             "_gvid": 0,
#             "tail": 0,
#             "head": 1,
#             "_draw_": [
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "b",
#                     "points": [
#                         [
#                             144.0,
#                             179.88
#                         ],
#                         [
#                             144.0,
#                             171.39
#                         ],
#                         [
#                             144.0,
#                             162.67
#                         ],
#                         [
#                             144.0,
#                             154.06
#                         ]
#                     ]
#                 }
#             ],
#             "_hdraw_": [
#                 {
#                     "op": "S",
#                     "style": "solid"
#                 },
#                 {
#                     "op": "c",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "C",
#                     "grad": "none",
#                     "color": "#000000"
#                 },
#                 {
#                     "op": "P",
#                     "points": [
#                         [
#                             147.5,
#                             154.0
#                         ],
#                         [
#                             144.0,
#                             144.0
#                         ],
#                         [
#                             140.5,
#                             154.0
#                         ]
#                     ]
#                 }
#             ],
#             "pos": "e,144,144 144,179.88 144,171.39 144,162.67 144,154.06"
#         }
#     ]
# }


def get_layout_definition_from_grid_layout_dict(
    obj: dict, job_group: JobGroupWithInstances
) -> LayoutDefinition:
    definition_index = {x.resource_id: x for x in job_group.job_instances}

    return LayoutDefinition(
        resource_id=NameUtils.get_anonymous_name("LayoutDefinition"),
        window_definition=get_window_definition_from_grid_layout_dict(
            obj, definition_index
        ),
    )


def get_window_definition_from_grid_layout_dict(
    obj: dict, definition_index: dict
) -> WindowDefinition:
    job_instances = {}
    items = {}
    sub_groups = {}
    external_groups = {}
    queues = {}

    queue_mapping = {}

    for x in obj["objects"]:
        queue_mapping[x["_gvid"]] = x["name"]

        if x["name"] in definition_index:
            job_instances[x["name"]] = (
                get_job_instance_position_definition_from_grid_layout_dict(x)
            )

        else:
            items[x["name"]] = get_item_position_definition_from_grid_layout_dict(x)

    for edge in obj.get("edges", []):
        head = edge["head"]
        tail = edge["tail"]

        tail_element_id = queue_mapping[tail]
        head_element_id = queue_mapping[head]

        if queues.get(edge["resource_id"]):
            queues[edge["resource_id"]].connections.append(
                (tail_element_id, head_element_id)
            )
            continue

        queue = get_queue_position_definition_from_grid_layout_dict(
            edge, tail_element_id, head_element_id, edge["resource_id"]
        )
        queues[queue.resource_id] = queue

    return WindowDefinition.model_construct(
        resource_id=NameUtils.get_anonymous_name("WindowDefinition"),
        job_instances=job_instances,
        queues=queues,
        sub_groups=sub_groups,
        items=items,
        external_groups=external_groups,
    )


def get_job_instance_position_definition_from_grid_layout_dict(obj: dict):
    return JobInstancePositionDefinition(
        resource_id=obj["name"],
        x=float(obj["pos"].split(",")[0]),
        y=float(obj["pos"].split(",")[1]),
        width=float(obj["width"]),
        height=float(obj["height"]),
        representation=obj["representation"],
    )


def get_item_position_definition_from_grid_layout_dict(obj: dict):
    return ItemPositionDefinition.model_construct(
        resource_id=obj["name"],
        x=float(obj["pos"].split(",")[0]),
        y=float(obj["pos"].split(",")[1]),
        width=float(obj["width"]),
        height=float(obj["height"]),
        resource_name=obj["label"],
        representation=obj["representation"],
    )


def get_queue_position_definition_from_grid_layout_dict(
    obj: dict, tail_element_id: str, head_element_id: str, queue_id: str
):
    return QueuePositionDefinition.model_construct(
        resource_id=queue_id,
        connections=[(tail_element_id, head_element_id)],
        representation=obj["representation"],
    )
