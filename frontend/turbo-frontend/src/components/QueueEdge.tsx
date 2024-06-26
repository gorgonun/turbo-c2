import { Box, Divider, Stack, Typography } from "@mui/material";
import { FC, useEffect, useState } from "react";
import {
  EdgeProps,
  getBezierPath,
  EdgeLabelRenderer,
  BaseEdge,
  getStraightPath,
} from "reactflow";
import { getAggregatedMetricByQueue } from "../api/prometheus-api";

interface Props {
  queueName: string;
  itemsQueuedCount: number;
}

const QueueEdge: FC<EdgeProps<Props>> = ({
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
  
  const { queueName, itemsQueuedCount } = data || {
    queueName: "No data",
    itemsQueuedCount: 0,
  };

  return (
    <>
      <BaseEdge id={id} path={edgePath} />
      <EdgeLabelRenderer>
        <Stack
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            background: "white",
            border: "1px solid #777",
            padding: 5,
            borderRadius: 5,
            fontSize: 10,
            fontWeight: 700,
            minWidth: 100,
          }}
        >
          <Box display='flex' justifyContent='center'><Typography fontSize={8} fontWeight={600}>{queueName}</Typography></Box>
          <Box py={0.1}>
            <Divider sx={{ color: 'black' }} />
          </Box>
          <Box display='flex' justifyContent='space-between'>
            <Typography fontSize={8}>Queued</Typography>
            <Typography fontSize={8}>{itemsQueuedCount}</Typography>
          </Box>
        </Stack>
      </EdgeLabelRenderer>
    </>
  );
};

export default QueueEdge;
