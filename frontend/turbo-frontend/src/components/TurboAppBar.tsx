import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
} from "@mui/material";
import JobModal from "./modals/JobModal";
import { JobIcon } from "../theme/icons";
import { useState } from "react";
import { useDraggable } from "@dnd-kit/core";
import TurboDrawer from "./TurboDrawer";
import RefreshIcon from '@mui/icons-material/Refresh';

export interface MetricsRefetchTimeMillsOption {
  value: number;
  label: { minimized: string; full: string };
}

interface Props {
  metricsRefetchTimeMills: MetricsRefetchTimeMillsOption;
  metricsRefetchTimeMillsOptions: MetricsRefetchTimeMillsOption[];
  handleSetMetricsRefetchTimeMillsOption: (optionValue: number) => void;
}

export default function TurboAppBar({
  metricsRefetchTimeMills,
  metricsRefetchTimeMillsOptions,
  handleSetMetricsRefetchTimeMillsOption,
}: Props) {
  const [openJobModal, setOpenJobModal] = useState(false);
  const [turboDrawerOpen, setTurboDrawerOpen] = useState(false);

  const {
    attributes: createJobAttributes,
    listeners: createJobListeners,
    setNodeRef: setCreateJobNodeRef,
    isDragging: isCreateJobDragging,
  } = useDraggable({
    id: "create-job-draggable",
    data: {
      eventType: "createJobDragged",
    },
  });

  const getHumanReadableTimeOptions = () => {
    return (
      <FormControl>
        <InputLabel disableAnimation={true}><RefreshIcon sx={{ color: 'white' }} /></InputLabel>
        <Select
          value={metricsRefetchTimeMills.value}
          label={metricsRefetchTimeMills.label.full}
          onChange={(event) =>
            handleSetMetricsRefetchTimeMillsOption(+event.target.value)
          }
          variant='outlined'
          sx={{
            color: "white",
            '.MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(228, 219, 233, 0.25)',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(228, 219, 233, 0.25)',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(228, 219, 233, 0.25)',
            },
            '.MuiSvgIcon-root ': {
              fill: "white !important",
            }
          }}
        >
          {metricsRefetchTimeMillsOptions.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label.minimized}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  };

  return (
    <Box>
      <AppBar position="sticky" color='primary'>
        <Toolbar sx={{ minHeight: '102px'}}>
          <IconButton
            size="large"
            color="inherit"
            onClick={() => setTurboDrawerOpen(true)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Box>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Turbo C2
            </Typography>
          </Box>
          <Stack ml={20} direction='row' flexGrow={1}>
            <Stack mt={2} mb={2} direction="row">
              <Box
                style={{ opacity: isCreateJobDragging ? 0.5 : 1 }}
                ref={setCreateJobNodeRef}
                {...createJobListeners}
                {...createJobAttributes}
              >
                <IconButton color="inherit">
                  <Box>
                    <JobIcon />
                    <Typography>Add job</Typography>
                  </Box>
                </IconButton>
              </Box>
            </Stack>
          </Stack>
          <Stack>
            <Stack>
              <Box>{getHumanReadableTimeOptions()}</Box>
            </Stack>
          </Stack>
        </Toolbar>
        <TurboDrawer open={turboDrawerOpen} handleDrawerClose={() => setTurboDrawerOpen(false)} />
      </AppBar>
      {openJobModal && <JobModal />}
    </Box>
  );
}
