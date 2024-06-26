import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import ReactFlow, {
  Background,
  Controls,
  Edge,
  Node,
  MiniMap,
  useReactFlow,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import JobNode from "./JobNode";
import QueueEdge from "./QueueEdge";
import EmptyJobNode from "./EmptyJobNode";
import {
  DragEndEvent,
  DragMoveEvent,
  DragStartEvent,
  Translate,
  useDroppable,
} from "@dnd-kit/core";
import { Box } from "@mui/material";
import DecisionNode from "./DecisionNode";
import ConditionEdge from "./conditionEdge";
import { TDraggableEvent } from "../domain/draggable-event";
import CreateJobModal from "./modals/CreateJobModal";
import { move_element } from "../api/turbo-api";
import useMousePosition from "../hooks/use-mouse-position";
import { getAggregatedMetricByGroup } from "../api/prometheus-api";
import { MetricsAggregated } from "../domain/metrics-aggregated";
import { QueueNode } from "./QueueNode";

interface Props {
  initialNodes: Node[];
  initialEdges: Edge[];
  createJobEvents: {
    event: TDraggableEvent;
    reason: "start" | "end" | "move" | "cancel";
  }[];
  moveJobEvents: {
    event: TDraggableEvent;
    reason: "start" | "end" | "move" | "cancel";
  }[];
  layoutId: string;
  setRefetch: (refetch: boolean) => void;
  groupPath: string;
  zoom: number;
  defaultCoordinates: Translate;
  metricsRefetchTimeMills: number;
}

const emptyJobNodeWH = {
  width: 220,
  height: 120,
}

function NodeEditor({
  initialNodes,
  initialEdges,
  createJobEvents,
  moveJobEvents,
  layoutId,
  groupPath,
  metricsRefetchTimeMills,
  setRefetch,
}: Props) {
  const nodeTypes = useMemo(
    () => ({
      jobNode: JobNode,
      emptyJobNode: EmptyJobNode,
      decisionNode: DecisionNode,
      queueNode: QueueNode,
    }),
    []
  );
  const edgeTypes = useMemo(
    () => ({ queueEdge: QueueEdge, conditionEdge: ConditionEdge }),
    []
  );
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const { setNodeRef } = useDroppable({
    id: "graph-grid",
  });
  const [nodeType, setNodeType] = useState<string | null>(null);
  const [jobIndex, setJobIndex] = useState(0);
  const [openCreateJobModal, setOpenCreateJobModal] = useState(false);
  const reactFlowInstance = useReactFlow();
  const mousePosition = useMousePosition();
  const [currentMovingNode, setCurrentMovingNode] = useState<Node | null>(null);
  const [originalNode, setOriginalNode] = useState<Node | null>(null);
  const [currentNewJobNode, setCurrentNewJobNode] = useState<Node | null>(null);

  const setMetrics = (metrics: MetricsAggregated) => {
    setNodes((nds) => {
      return nds.map((nd) => {
        // FIXME: Cannot be undefined
        if (nd != undefined) {
          const metric = metrics[nd.id];

          if (metrics != undefined) {
            if (nd.type === 'jobNode') {
              const replicas = (metric?.replicas ?? [0, 0])[1];
              const inputCount = (metric?.input ?? [0, 0])[1];
              const outputCount = (metric?.output ?? [0, 0])[1];
    
              return {
                ...nd,
                data: {
                  ...nd.data,
                  replicas,
                  inputCount,
                  outputCount,
                },
              }
            } else if (nd.type === 'queueNode') {
              const count = (metric?.input ?? [0, 0])[1];
              return {
                ...nd,
                data: {
                  ...nd.data,
                  itemsQueuedCount: count,
                },
              };
            }
          }

          return nd;
        }
      });
    });

    for (const edge of edges) {
      const metric = metrics[edge.id];

      if (metric != undefined) {
        const count = (metric?.input ?? [0, 0])[1];

        setEdges((eds) => {
          return eds.map((ed) => {
            if (ed.id === edge.id) {
              return {
                ...ed,
                data: {
                  ...ed.data,
                  itemsQueuedCount: count,
                },
              };
            }
            return ed;
          });
        });
      }
    }
  }

  useEffect(() => {
    const getMetrics = () => {
      getAggregatedMetricByGroup(groupPath).then((metrics) => setMetrics(metrics));
    }

    getMetrics();

    const interval = setInterval(getMetrics, metricsRefetchTimeMills);
    return () => clearInterval(interval);
  }, [metricsRefetchTimeMills]);

  useEffect(() => {
    if (createJobEvents.length > 0) {
      const createJobEvent = createJobEvents.pop();

      if (createJobEvent == undefined) {
        console.error("createJobEvent is undefined");
        return;
      }

      const { event, reason } = createJobEvent;

      switch (reason) {
        case "start":
          handleCreateJobDraggedStart();
          break;
        case "move":
          handleCreateJobOnDragMove(event as DragMoveEvent);
          break;
        case "end":
          handleCreateJobDraggedEnd(event as DragMoveEvent);
          break;
        case "cancel":
          handleCreateJobOnDragCancel();
          break;
        default:
          console.error("Unknown event reason");
          break;
      }
    }
  }, [createJobEvents]);

  useEffect(() => {
    if (moveJobEvents.length > 0) {
      const event = moveJobEvents[moveJobEvents.length - 1].event;
      const reason = moveJobEvents[moveJobEvents.length - 1].reason;

      switch (reason) {
        case "start":
          handleMoveJobStart(event as DragStartEvent);
          break;
        case "move":
          handleMoveJobMove(event as DragMoveEvent);
          break;
        case "end":
          handleMoveJobEnd(event as DragEndEvent);
          break;
        case "cancel":
          handleMoveJobCancel();
          break;
        default:
          console.error("Unknown event reason");
          break;
      }
    }
  }, [moveJobEvents]);

  const handleCreateJobDraggedEnd = (event: DragMoveEvent) => {
    // FIXME
    // if (event.over && event.over.id === "graph-grid") {
    setJobIndex((i) => i + 1);
    setOpenCreateJobModal(true);
    // }
  };

  const handleCreateJobDraggedStart = () => {
    if (mousePosition.x == null || mousePosition.y == null) {
      console.error("mousePosition is null");
      return;
    }

    const position = {
      x: mousePosition.x - emptyJobNodeWH.width / 2,
      y: mousePosition.y - emptyJobNodeWH.height / 2,
    };

    const newNode = {
      id: `new-job-${jobIndex}`,
      type: "emptyJobNode",
      position,
      height: 100,
      width: 200,
    } as Node;

    setNodes((nds) => nds.concat(newNode));
    setCurrentNewJobNode(newNode);
  };

  const handleCreateJobOnDragMove = (event: DragMoveEvent) => {
    setNodes((nds) => {
      if (currentNewJobNode == null) {
        console.error("currentNewJobNode is null");
        return nds;
      }

      return nds.map((node) => {
        if (node.id === currentNewJobNode.id) {
          return {
            ...node,
            position: reactFlowInstance.screenToFlowPosition({
              x: currentNewJobNode.position.x + event.delta.x,
              y: currentNewJobNode.position.y + event.delta.y,
            }),
          };
        }
        return node;
      }
      );
    });
  };

  const handleCreateJobOnDragCancel = () => {
    setNodeType(null);
    setNodes((nds) => nds.slice(0, nds.length - 1));
    reactFlowInstance.deleteElements({ nodes: [{ id: `new-job-${jobIndex - 1}` }] });
  };

  const handleMoveJobStart = (event: DragStartEvent) => {
    const elementId = event.active.id as string;
    const node = nodes.find((node) => node.id === elementId);

    if (node == undefined) {
      console.error("node is undefined");
      return;
    }

    setCurrentMovingNode(node);
    setOriginalNode(node);
  };

  const handleMoveJobMove = (event: DragMoveEvent) => {
    setCurrentMovingNode((node) => {
      if (node == null) {
        console.error("node is null");
        return node;
      }

      return {
        ...node,
        position: { x: node.position.x + event.delta.x, y: node.position.y + event.delta.y},
      };
    });
  };

  const handleMoveJobEnd = async (event: DragEndEvent) => {
    const elementId = event.active.id as string;

    if (elementId == undefined) {
      console.error("elementId is undefined");
      return;
    }

    const node = nodes.find((node) => node.id === elementId);

    if (node == undefined) {
      console.error("node is undefined");
      return;
    }

    if (originalNode == null) {
      console.error("originalNode is null");
      return;
    }

    const elements = {
      [`${elementId}`]: {
        element_type: "job_instances",
        position_definition: {
          x: node.position.x,
          y: node.position.y,
        },
      },
    }

    await move_element(layoutId, elements);
    setRefetch(true);
  };

  const handleMoveJobCancel = () => {
    setCurrentMovingNode(null);
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const currentCreateNode = currentNewJobNode && nodes.find((node) => node.id === currentNewJobNode.id);

  return (
    <Box ref={setNodeRef} width="100%" height="100%">
      <ReactFlow
        fitView
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        proOptions={{ hideAttribution: true }}
        nodesDraggable
        nodes={nodes}
        edges={edges}
        onConnect={onConnect}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
      >
        <MiniMap zoomable pannable />
        <Background />
        <Controls />
      </ReactFlow>
      {openCreateJobModal && currentCreateNode && (
        <CreateJobModal
          open={true}
          onClose={() => {
            handleCreateJobOnDragCancel();
            setOpenCreateJobModal(false);
          }}
          onCreateJob={() => setRefetch(true)}
          groupPath={groupPath}
          layoutId={layoutId}
          positionDefinition={currentCreateNode.position}
        />
      )}
    </Box>
  );
}

export default NodeEditor;
