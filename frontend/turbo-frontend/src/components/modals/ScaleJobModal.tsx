import {
  Box,
  Button,
  Modal,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { scaleJobInstance } from "../../api/turbo-api";
import { useState } from "react";
import CustomIconButton from "../CustomIconButton";
import CloseIcon from "@mui/icons-material/Close";

interface Props {
  instanceId: string;
  replicas: number;
  onClose: () => void;
}

export const ScaleJobModal = ({
  instanceId,
  replicas,
  onClose,
}: Props) => {
  const [newReplicas, setNewReplicas] = useState(replicas);

  return (
    <Modal open={true} onClose={onClose}>
      <Stack
        sx={{
          minWidth: 300,
          minHeight: 400,
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          bgcolor: "white",
          border: "2px solid #000",
          boxShadow: 24,
          p: 4,
        }}
      >
        <Stack alignItems="end">
          <CustomIconButton icon={<CloseIcon />} onClick={onClose} />
        </Stack>
        <Box>
          <Typography variant="h6">Scale job</Typography>
        </Box>
        <Stack mt={2}>
          <TextField
            label="Replicas"
            value={newReplicas}
            onChange={(event) => setNewReplicas(Number.parseInt(event.target.value))}
            type='number'
          />
        </Stack>
        <Stack flexDirection='column-reverse' flexGrow={1} height='100%'>
          <Button
            onClick={() => {
              scaleJobInstance(instanceId, newReplicas);
              onClose();
            }}
            disabled={newReplicas === replicas}
            fullWidth
          >
            Scale
          </Button>
        </Stack>
        </Stack>
    </Modal>
  );
};
