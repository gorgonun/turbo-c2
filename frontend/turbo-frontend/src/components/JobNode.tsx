import {
  Box,
  Divider,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { Handle, NodeProps, Position } from "reactflow";
import { JobIcon } from "../theme/icons";
import PlayArrowSharpIcon from "@mui/icons-material/PlayArrowSharp";
import PauseSharpIcon from "@mui/icons-material/PauseSharp";
import StopSharpIcon from "@mui/icons-material/StopSharp";
import AddSharpIcon from "@mui/icons-material/AddSharp";
import { useDraggable } from "@dnd-kit/core";

interface Props {
  instanceId: string;
  instanceName: string;
  definitionName: string;
  replicas: number;
  isPaused: boolean;
  inputCount: number;
  outputCount: number;
  runningTime: number;
  onScaleClick: (instanceId: string, replicas: number) => void;
  onPlayClick: (instanceId: string, replicas: number) => void;
  onPauseClick: (instanceId: string) => void;
  onResumeClick: (instanceId: string) => void;
}

export default function JobNode({ data }: NodeProps<Props>) {
  const {
    instanceId,
    instanceName,
    definitionName,
    replicas,
    isPaused,
    inputCount,
    outputCount,
    runningTime,
    onScaleClick,
    onPlayClick,
    onPauseClick,
    onResumeClick,
  } = data;

  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: instanceId,
    data: {
      eventType: "jobDragged",
    },
  });

  return (
    <Box
      sx={{
        background: "white",
        border: "1px solid #777",
        borderRadius: 2,
        padding: 0.3,
        width: 200,
        maxHeight: 120,
      }}
      style={{ opacity: isDragging ? 0.5 : 1 }}
      ref={setNodeRef}
      {...listeners}
      {...attributes}
    >
      <Box>
        <Stack>
          <Box display="flex" alignItems="center">
            <JobIcon sx={{ color: "lightGray", fontSize: 16, mx: 0.3 }} />
            <Typography
              fontSize={12}
              fontWeight={600}
              textOverflow="ellipsis"
              noWrap
            >
              {instanceName}
            </Typography>
          </Box>
          <Box py={0.1}>
            <Divider sx={{ color: "black" }} />
          </Box>
          <Stack direction="row" justifyContent="space-evenly">
            <Tooltip
              title={
                replicas === 0
                  ? "Start job with 1 replica"
                  : `Job running with ${replicas} ${
                      replicas === 1 ? "replica" : "replicas"
                    }`
              }
              arrow
            >
              <IconButton
                onClick={() => isPaused ? onResumeClick(instanceId) : onPlayClick(instanceId, 1)}
                sx={{ padding: 0 }}
                disabled={replicas > 0}
              >
                <PlayArrowSharpIcon
                  sx={{
                    color: replicas === 0 ? "lightGray" : "green",
                    fontSize: 16,
                    "&:hover": {
                      color: "green",
                    },
                  }}
                />
              </IconButton>
            </Tooltip>
            <IconButton
              onClick={() => onPauseClick(instanceId)}
              sx={{ padding: 0 }}
              disabled={isPaused}
            >
              <PauseSharpIcon
                sx={{ color: isPaused ? "orange" : "lightGray", fontSize: 16 }}
              />
            </IconButton>

            <StopSharpIcon
              sx={{ color: replicas === 0 ? "red" : "lightGray", fontSize: 16 }}
            />
            <IconButton
              onClick={() => onScaleClick(instanceId, replicas)}
              sx={{ padding: 0 }}
            >
              <AddSharpIcon sx={{ color: "black", fontSize: 16 }} />
            </IconButton>
          </Stack>
          <Box py={0.1}>
            <Divider sx={{ color: "black" }} />
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography fontSize={8} fontWeight={600}>
              Definition:
            </Typography>
            <Typography fontSize={8}>{definitionName}</Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography fontSize={8} fontWeight={600}>
              Replicas:
            </Typography>
            <Typography fontSize={8}>{replicas}</Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography fontSize={8} fontWeight={600}>
              In:
            </Typography>
            <Typography fontSize={8}>{inputCount}</Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography fontSize={8} fontWeight={600}>
              Out:
            </Typography>
            <Typography fontSize={8}>{outputCount}</Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography fontSize={8} fontWeight={600}>
              Runtime:
            </Typography>
            <Typography fontSize={8}>{runningTime}</Typography>
          </Box>
        </Stack>
      </Box>
      <Handle id="1" type="target" position={Position.Bottom} />
      <Handle id="2" type="source" position={Position.Top} />
    </Box>
  );
}
