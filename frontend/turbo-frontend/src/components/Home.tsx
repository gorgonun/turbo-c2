/* eslint-disable */
import { Box, Stack } from "@mui/material";
import NodeEditor from "./NodeEditor";
import { getJobGroup, pauseJobInstance, resumeJobInstance, scaleJobInstance } from "../api/turbo-api";
import {
  Edge,
  MarkerType,
  Node,
  ReactFlowProvider,
  useReactFlow,
  useViewport,
} from "reactflow";
import { useEffect, useState } from "react";
import TurboAppBar, { MetricsRefetchTimeMillsOption } from "./TurboAppBar";
import {
  Active,
  DndContext,
  DragCancelEvent,
  DragEndEvent,
  DragMoveEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  ItemPositionDefinition,
  JobInstancePositionDefinition,
  PositionDefinition,
  EdgeRepresentation,
  HasNodeRepresentation,
  HasEdgeRepresentation,
} from "../domain/layout-definition";
import { JobInstance } from "../domain/job-instance";
import { TDraggableEvent } from "../domain/draggable-event";
import TurboLowBar from "./TurboLowBar";
import humanizeDuration from "humanize-duration";
import { getHumanReadableTime } from "../helpers/human-readable-time";
import { calculateElementPosition } from "../helpers/calculate-position-between-grid-elements";
import { ScaleJobModal } from "./modals/ScaleJobModal";
import { LayoutGrid } from "../domain/layout-grid";

function hasRepresentation(
  it: any
): it is HasNodeRepresentation | HasEdgeRepresentation {
  return (
    (it as HasNodeRepresentation | HasEdgeRepresentation).representation !==
    undefined
  );
}

const Home = () => {
  const [dataFetched, setDataFetched] = useState(false);
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [groupData, setGroupData] = useState<any | null>(null);
  const [subgroupData, setSubgroupData] = useState<any | null>(null);
  const [createJobEvents, setCreateJobEvents] = useState<
    { event: TDraggableEvent; reason: "start" | "end" | "move" | "cancel" }[]
  >([]);
  const [moveJobEvents, setMoveJobEvents] = useState<
    { event: TDraggableEvent; reason: "start" | "end" | "move" | "cancel" }[]
  >([]);
  const [layoutId, setLayoutId] = useState<string | null>(null);
  const [refetch, setRefetch] = useState(false);
  const [fetchingData, setFetchingData] = useState(false);
  const [groupPath, setGroupPath] = useState("root");
  const [metricsRefetchTimeMills, setMetricsRefetchTimeMills] =
    useState<MetricsRefetchTimeMillsOption>({
      value: 5 * 1000,
      label: getHumanReadableTime(5 * 1000),
    });
  const [scaleJobModalOpen, setScaleJobModalOpen] = useState(false);
  const [scaleJobData, setScaleJobData] = useState<{
    instanceId: string;
    replicas: number;
  } | null>(null);
  const reactFlowInstance = useReactFlow();

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  useEffect(() => {
    setFetchingData(true);
    getJobGroup(groupPath).then((r) => handleLayoutData(r));
    console.log("Fetching data");
  }, [])

  useEffect(() => {
    if (refetch && !fetchingData) {
      console.log({ refetch, groupPath, fetchingData })
      setDataFetched(false);
      setFetchingData(true);

      getJobGroup(groupPath).then((r) => handleLayoutData(r));
      setRefetch(false);
    }
  }, [refetch, groupPath]);

  function handleLayoutData(data: LayoutGrid) {
    setLayoutId(data.layout_definition.resource_id);

    const groupDataWithMapping = {
      ...data.group,
      job_instances_mapping: data.group.job_instances.reduce(
        (acc: Record<string, JobInstance>, job_instance) => ({
          ...acc,
          [job_instance.resource_id]: job_instance,
        }),
        {}
      ),
    };

    setGroupData(groupDataWithMapping);

    setSubgroupData(
      Object.values(data.subgroups).map((i: any) => ({
        ...i.group_data,
        job_instances_mapping: i.group_data.job_instances
          .map((i: any) => [i.resource_id, i])
          .reduce((acc: any, [k, v]: any) => ({ ...acc, [k]: v }), {}),
      }))
    );

    const nodes: (
      | ItemPositionDefinition
      | JobInstancePositionDefinition
      | PositionDefinition
    )[] = [
      ...Object.values(data.layout_definition.window_definition.job_instances),
      ...Object.values(data.layout_definition.window_definition.sub_groups),
      ...Object.values(data.layout_definition.window_definition.items),
      ...Object.values(
        data.layout_definition.window_definition.external_groups
      ),
    ];

    setNodes(
      nodes.map((position_definition) => {
        const instance =
          groupDataWithMapping.job_instances_mapping[
            position_definition.resource_id
          ];

        if (instance !== undefined) {
          return {
            id: "" + position_definition.resource_id,
            data: {
              instanceId: instance.resource_id,
              instanceName: instance.name,
              definitionName: instance.job_definition,
              replicas: instance.replicas,
              isPaused: data.instances_data[instance.resource_id]?.state === "paused",
              inputCount: 0,
              outputCount: 0,
              runningTime: 0,
              onScaleClick: (instanceId: string, replicas: number) => {
                setScaleJobData({ instanceId, replicas });
                setScaleJobModalOpen(true);
              },
              onPlayClick: (instanceId: string, replicas: number) => {
                scaleJobInstance(instanceId, replicas);
              },
              onPauseClick: (instanceId: string) => {
                pauseJobInstance(instanceId);
              },
              onResumeClick: (instanceId: string) => {
                resumeJobInstance(instanceId);
              }
            },
            position: {
              x: +position_definition.x,
              y: +position_definition.y,
            },
            height: +position_definition.height,
            width: +position_definition.width,
            type: "jobNode",
          } as Node;
        } else if (
          hasRepresentation(position_definition) &&
          position_definition.representation === "DECISION"
        ) {
          return {
            id: "" + position_definition.resource_id,
            data: {
              name: position_definition.resource_id,
            },
            position: {
              x: +position_definition.x,
              y: +position_definition.y,
            },
            height: +position_definition.height,
            width: +position_definition.width,
            type: "decisionNode",
          } as Node;
        } else {
          console.error("Unknown position_definition", position_definition);
        }
      })
    );

    if (
      Object.keys(data.layout_definition.window_definition.queues).length > 0
    ) {
      setEdges(
        Object.values(data.layout_definition.window_definition.queues).flatMap(
          (it) => {
            if (it.representation === EdgeRepresentation.QUEUE) {
              const positions = it.connections
                .flat()
                .flatMap(
                  (nodeId) => reactFlowInstance.getNode(nodeId) ?? []
                )
                // Need to get the node position (left upper edge) + half of the node width and height (fix edge) and subtract the half of the queue node width and height
                .map((node) => ({
                  x: node.position.x + (node?.width ?? 0) / 2 - 75,
                  y: node.position.y + (node?.height ?? 0) / 2 - 25,
                }));

              const middle = calculateElementPosition(positions);

              const newQueueNode = {
                id: it.resource_id,
                data: {
                  queueName: it.resource_id,
                  itemsQueuedCount: 0,
                },
                position: {
                  x: middle.x,
                  y: middle.y,
                },
                type: "queueNode",
              };
              reactFlowInstance.addNodes([newQueueNode]);

              const ids = new Set();

              return it.connections.flatMap(([src, tgt]) => {
                const srcId = `${src}_${it.resource_id}`;
                const tgtId = `${it.resource_id}_${tgt}`;
                const result = [];

                if (!ids.has(srcId)) {
                  result.push({
                    id: srcId,
                    source: src,
                    target: it.resource_id,
                    type: "straight",
                  });
                  ids.add(srcId);
                }

                if (!ids.has(tgtId)) {
                  result.push({
                    id: tgtId,
                    source: it.resource_id,
                    target: tgt,
                    type: "straight",
                  });
                  ids.add(tgtId);
                }

                ids.add(srcId);
                ids.add(tgtId);

                return result;
              });
            } else if (
              it["representation"] === EdgeRepresentation.CONDITION_TRUE
            ) {
              return [
                {
                  id: it.resource_id,
                  source: it.connections[0][0],
                  target: it.connections[0][1],
                  type: "conditionEdge",
                  markerEnd: {
                    type: MarkerType.Arrow,
                    width: 50,
                    height: 50,
                    color: "#FF0072",
                  },
                  data: {
                    condition: true,
                  },
                },
              ];
            } else if (it.representation === EdgeRepresentation.EXECUTION) {
              return [
                {
                  id: it.resource_id,
                  source: it.connections[0][0],
                  target: it.connections[0][1],
                  type: "straight",
                },
              ];
            } else {
              console.error("Unknown edge representation", it);
              return [];
            }
          }
        )
      );
    }

    setDataFetched(true);
    setFetchingData(false);
  }

  function handleDrag<T extends { active: Active }>(
    event: T,
    handleEvent: (eventType: string) => void
  ) {
    const eventType = event.active.data.current?.eventType;

    if (eventType == undefined) {
      console.error("eventType is undefined");
      return;
    }

    return handleEvent(eventType);
  }

  const handleDragEnd = (event: DragEndEvent) => {
    return handleDrag(event, (eventType) =>
      eventMapping[eventType]({ event, reason: "end" })
    );
  };

  const handleDragStart = (event: DragStartEvent) => {
    return handleDrag(event, (eventType) =>
      eventMapping[eventType]({ event, reason: "start" })
    );
  };

  const handleOnDragMove = (event: DragMoveEvent) => {
    return handleDrag(event, (eventType) =>
      eventMapping[eventType]({ event, reason: "move" })
    );
  };

  const handleOnDragCancel = (event: DragCancelEvent) => {
    return handleDrag(event, (eventType) =>
      eventMapping[eventType]({ event, reason: "cancel" })
    );
  };

  const eventMapping: Record<
    string,
    (event: {
      event: TDraggableEvent;
      reason: "start" | "end" | "move" | "cancel";
    }) => void
  > = {
    createJobDragged: (event) =>
      setCreateJobEvents((events) => events.concat(event)),
    jobDragged: (event) => setMoveJobEvents((events) => events.concat(event)),
  };

  const metricsRefetchTimeMillsOptions = () => {
    return [1, 2, 3, 4, 5, 10, 15, 20, 30, 60].map((i) => {
      const value = i * 1000;
      return {
        value,
        label: getHumanReadableTime(value),
      };
    });
  };

  const handleSetMetricsRefetchTimeMillsOption = (value: number) => {
    setMetricsRefetchTimeMills({ value, label: getHumanReadableTime(value) });
  };

  return (
    <DndContext
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragMove={handleOnDragMove}
      onDragCancel={handleOnDragCancel}
      sensors={sensors}
    >
      <Stack style={{ width: "100%", height: "100%" }}>
        <Box>
          <TurboAppBar
            metricsRefetchTimeMills={metricsRefetchTimeMills}
            metricsRefetchTimeMillsOptions={metricsRefetchTimeMillsOptions()}
            handleSetMetricsRefetchTimeMillsOption={
              handleSetMetricsRefetchTimeMillsOption
            }
          />
        </Box>
        <DragOverlay>
          <Box></Box>
        </DragOverlay>
        {dataFetched && (
          <Box style={{ width: "100%", height: "100%" }}>
            <NodeEditor
              initialNodes={nodes}
              initialEdges={edges}
              createJobEvents={createJobEvents}
              moveJobEvents={moveJobEvents}
              layoutId={layoutId}
              setRefetch={setRefetch}
              groupPath={groupPath}
              metricsRefetchTimeMills={metricsRefetchTimeMills.value}
            />
          </Box>
        )}
        {!dataFetched && (
          <Stack style={{ width: "100%", height: "100%" }}>
            <Box>Loading...</Box>
          </Stack>
        )}
        <TurboLowBar
          groupPath={groupPath}
          handleGoToGroup={(group) => {
            setRefetch(true);
            setGroupPath(group);
          }}
        />
      </Stack>
      {scaleJobModalOpen && (
        <ScaleJobModal
          instanceId={scaleJobData?.instanceId ?? ""}
          replicas={scaleJobData?.replicas ?? 0}
          onClose={() => setScaleJobModalOpen(false)}
        />
      )}
    </DndContext>
  );
};

const HomeWithProvider = () => {
  return (
    <ReactFlowProvider>
      <Home />
    </ReactFlowProvider>
  );
};

export default HomeWithProvider;
