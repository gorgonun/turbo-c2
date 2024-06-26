import { Box, Divider, Stack, Typography } from "@mui/material";
import { FC } from "react";
import { NodeProps, Handle, Position } from "reactflow";

interface Props {
  queueName: string;
  itemsQueuedCount: number;
}

export const QueueNode: FC<NodeProps<Props>> = ({
  data: { queueName, itemsQueuedCount },
}) => {
  return (
    <>
      <Stack
        sx={{
          background: "white",
          border: "1px solid #777",
          padding: 1,
          borderRadius: 2,
          fontSize: 10,
          fontWeight: 700,
          width: 150,
          height: 50,
        }}
      >
        <Box display="flex" justifyContent="center">
          <Typography fontSize={8} fontWeight={600} textOverflow='ellipsis' noWrap>
            {queueName}
          </Typography>
        </Box>
        <Box py={0.1}>
          <Divider sx={{ color: "black" }} />
        </Box>
        <Box display="flex" justifyContent="space-between">
          <Typography fontSize={8}>Queued</Typography>
          <Typography fontSize={8}>{itemsQueuedCount}</Typography>
        </Box>
        <Handle type="target" position={Position.Bottom} />
        <Handle type="source" position={Position.Top} />
      </Stack>
    </>
  );
};
