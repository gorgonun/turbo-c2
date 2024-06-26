import { Box, Divider, Stack, Tooltip, Typography } from "@mui/material";
import { Handle, Position } from "reactflow";
import { JobIcon } from "../theme/icons";
import PlayArrowSharpIcon from "@mui/icons-material/PlayArrowSharp";
import PauseSharpIcon from "@mui/icons-material/PauseSharp";
import StopSharpIcon from "@mui/icons-material/StopSharp";
import AddSharpIcon from "@mui/icons-material/AddSharp";

export default function EmptyJobNode() {
  const { instanceName, definitionName, replicas, isPaused, inputCount, outputCount, runningTime } = {
    instanceName: "New Job",
    definitionName: "...",
    replicas: 0,
    isPaused: true,
    inputCount: 0,
    outputCount: 0,
    runningTime: 0,
  
  };
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
    >
      <Box>
        <Stack>
          <Box display="flex" alignItems="center">
            <JobIcon sx={{ color: "lightGray", fontSize: 16, mx: 0.3 }} />
            <Typography fontSize={12} fontWeight={600}>
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
              <PlayArrowSharpIcon
                sx={{
                  color: replicas === 0 ? "lightGray" : "green",
                  fontSize: 16,
                }}
              />
            </Tooltip>
            <PauseSharpIcon
              sx={{ color: isPaused ? "orange" : "lightGray", fontSize: 16 }}
            />
            <StopSharpIcon
              sx={{ color: replicas === 0 ? "red" : "lightGray", fontSize: 16 }}
            />
            <AddSharpIcon sx={{ color: "black", fontSize: 16 }} />
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
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Left} />
      <Handle type="source" position={Position.Right} />
    </Box>
  );
}
