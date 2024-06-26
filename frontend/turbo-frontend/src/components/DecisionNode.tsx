import { Box, Divider, Stack, Tooltip, Typography } from "@mui/material";
import { Handle, NodeProps, Position } from "reactflow";
import { JobIcon } from "../theme/icons";
import PlayArrowSharpIcon from "@mui/icons-material/PlayArrowSharp";
import PauseSharpIcon from "@mui/icons-material/PauseSharp";
import StopSharpIcon from "@mui/icons-material/StopSharp";
import AddSharpIcon from "@mui/icons-material/AddSharp";

interface Props {
  instanceName: string;
  definitionName: string;
  replicas: number;
  isPaused: boolean;
  inputCount: number;
  outputCount: number;
  runningTime: number;
}

export default function DecisionNode({ data }: NodeProps<Props>) {

  return (
    <Box
      sx={{
        background: "white",
        border: "1px solid #777",
        borderRadius: 2,
        minWidth: 75,
        maxWidth: 200,
        minHeight: 75,
        maxHeight: 120,
        transform: 'rotate(45deg)',
      }}
    >
      <Box>
        <Handle id="1" type="target" position={Position.Bottom} style={{ left: 0 }} />
        <Handle id="2" type="source" position={Position.Top} style={{ left: 70, bottom: 0 }} />
      </Box>
    </Box>
  );
}
