import { Box, Divider, Stack, Typography } from "@mui/material";
import { FC } from "react";
import {
  EdgeProps,
  getBezierPath,
  EdgeLabelRenderer,
  BaseEdge,
  MarkerType,
  getStraightPath,
} from "reactflow";

interface Props {
  condition: boolean;
}

const ConditionEdge: FC<EdgeProps<Props>> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}) => {
  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX,
    sourceY,
    // sourcePosition,
    targetX,
    targetY,
    // targetPosition,
  });

  const { condition } = data || {
    condition: true,
  };

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{ stroke: "green" }}
      />
    </>
  );
};

export default ConditionEdge;
