import {
  Box,
  Button,
  Card,
  CardActionArea,
  Checkbox,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Modal,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { create_job_instance, getDefinitions, listQueues } from "../../api/turbo-api";
import { useEffect, useState } from "react";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import CloseIcon from "@mui/icons-material/Close";
import CustomIconButton from "../CustomIconButton";
import validator from "@rjsf/validator-ajv8";
import { Definition } from "../../domain/definition";
import Form from "@rjsf/core";
import { JobInstanceDataRequest } from "../../domain/job-instance-data-request";
import { RemoteJobReplicaMode } from "../../domain/job-instance";
import { PositionDefinition } from "../../domain/layout-definition";

interface Props {
  open: boolean;
  groupPath: string;
  positionDefinition: Pick<PositionDefinition, "x" | "y">;
  layoutId: string;
  onClose: () => void;
  onCreateJob?: () => void;
}

const CreateJobModal = ({
  open,
  groupPath,
  positionDefinition,
  layoutId,
  onClose,
  onCreateJob,
}: Props) => {
  const [step, setStep] = useState(0);
  const [selectedDefinition, setSelectedDefinition] =
    useState<Definition | null>(null);

  const handleDefinitionSelection = (definition: Definition) => {
    setStep(1);
    setSelectedDefinition(definition);
  };

  const handleSetJobInstanceData = async (
    jobInstanceData: JobInstanceDataRequest
  ) => {
    await create_job_instance({
      ...jobInstanceData,
      position_definition: positionDefinition,
      layout_id: layoutId,
    });
    onClose();
    onCreateJob?.();
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Box
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
        {" "}
        <Stack alignItems="end">
          <CustomIconButton icon={<CloseIcon />} onClick={onClose} />
        </Stack>
        <Typography variant="h6">Create job</Typography>
        {step === 0 && (
          <ListDefinition
            onClose={onClose}
            onSelect={handleDefinitionSelection}
          />
        )}
        {step === 1 && (
          <CreateJobForm
            definition={selectedDefinition as Definition}
            groupPath={groupPath}
            setJobInstanceData={handleSetJobInstanceData}
          />
        )}
      </Box>
    </Modal>
  );
};

interface CreateJobFormProps {
  definition: Definition;
  groupPath: string;
  setJobInstanceData: (jobInstanceData: JobInstanceDataRequest) => void;
}

const CreateJobForm = ({
  definition,
  setJobInstanceData,
  groupPath,
}: CreateJobFormProps) => {
  const [fieldsValues, setFieldsValues] = useState(null);
  const [instanceName, setInstanceName] = useState("");
  const [replicas, setReplicas] = useState(1);
  const [readOnly, setReadOnly] = useState(false);
  const [inputQueueReference, setInputQueueReference] = useState<string | null>(
    null
  );
  const [extraQueueReferences, setExtraQueueReferences] = useState<string[]>(
    new Array(definition.parameters.queues.extra_queues?.quantity ?? 0)
  );
  const [outputQueueReferences, setOutputQueueReferences] = useState<string[]>(
    new Array(definition.parameters.queues.extra_queues?.quantity ?? 0)
  );
  const [currentQueues, setCurrentQueues] = useState<string[]>([]);
  
  useEffect(() => {
    listQueues().then((queues) => setCurrentQueues(queues)); 
  }, [])

  const handleCreate = () => {
    setJobInstanceData({
      job_definition_id: definition.name,
      name: instanceName,
      replicas: replicas,
      replication_mode: RemoteJobReplicaMode.MANUAL_SETTING,
      read_only: readOnly,
      group_path: groupPath,
      input_queue_reference: inputQueueReference,
      extra_queues_references: extraQueueReferences,
      output_queues_references: outputQueueReferences,
      parameters: fieldsValues,
    });
  };

  const extraQueues = new Array(
    definition.parameters.queues.extra_queues?.quantity ?? 0
  )
    .fill(null)
    .map((_, i) => i);

  const outputQueues = new Array(
    definition.parameters.queues.output_queues?.quantity ?? 0
  )
    .fill(null)
    .map((_, i) => i);

  const log = (type: any) => console.log.bind(console, type);

  return (
    <Box>
      <Box mt={1}>
        <Typography fontWeight={700}>Definition: {definition.name}</Typography>
      </Box>
      <Box mt={2}>
        <Box mt={1} p={2} sx={{ border: "1px solid black" }}>
          <Box textAlign="center">
            <Typography fontWeight={700}>Instance Data</Typography>
          </Box>
          <Stack mt={3}>
            <TextField
              label="Name"
              variant="standard"
              value={instanceName}
              onChange={(event) => setInstanceName(event.target.value)}
            />
          </Stack>
          <Stack mt={1}>
            <TextField
              type="number"
              label="replicas"
              variant="standard"
              value={replicas}
              onChange={(event) =>
                setReplicas(Number.parseInt(event.target.value))
              }
            />
          </Stack>
          <Stack
            direction="row"
            mt={1}
            justifyContent="space-between"
            alignItems="center"
          >
            <Typography fontSize="14px">Read only</Typography>
            <Checkbox
              onChange={(event) => setReadOnly(event.target.checked)}
              checked={readOnly}
            />
          </Stack>
          {definition.parameters.queues.input_queue && (
            <Stack mt={1}>
              {/* <TextField
                label="Input queue name"
                variant="standard"
                value={inputQueueReference}
                onChange={(event) => setInputQueueReference(event.target.value)}
              /> */}
              <FormControl>
                <InputLabel disableAnimation={true}>
                  Input queue name
                </InputLabel>
                <Select
                  value={inputQueueReference}
                  label={inputQueueReference ?? ""}
                  onChange={(event) =>
                    setInputQueueReference(event.target.value as string)
                  }
                  variant="outlined"
                >
                  {currentQueues.map((queue) => (
                    <MenuItem key={`input-option-${queue}`} value={queue}>
                      {queue}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          )}
          {extraQueues.length > 0 &&
            extraQueues.map((i) => (
              <Stack mt={1}>
                <TextField
                  label={`Extra queue name (${i + 1})`}
                  value={extraQueueReferences[i] ?? ""}
                  onChange={(event) =>
                    setExtraQueueReferences((prev) => {
                      prev[i] = event.target.value;
                      return prev;
                    })
                  }
                />
              </Stack>
            ))}
          {outputQueues.length > 0 &&
            outputQueues.map((i) => (
              <Stack mt={1}>
                {/* <TextField
                  label="Name"
                  value={outputQueueReferences[i] ?? ""}
                  onChange={(event) => {
                    setOutputQueueReferences((prev) => {
                      prev[i] = event.target.value;
                      return prev;
                    });
                  }}
                /> */}
                <FormControl>
                  <InputLabel disableAnimation={true}>
                    Output queue name ({i + 1})
                  </InputLabel>
                  <Select
                    value={outputQueueReferences[i] ?? null}
                    label={outputQueueReferences[i] ?? ""}
                    onChange={(event) =>
                      setOutputQueueReferences((prev) => {
                        prev[i] = event.target.value as string;
                        return prev;
                      })
                    }
                    variant="outlined"
                  >
                    {currentQueues.map((queue) => (
                      <MenuItem
                        key={`output-option-${queue}-${i}`}
                        value={queue}
                      >
                        {queue}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>
            ))}
        </Box>
        <Box mt={2}>
          {definition.parameters.fields && (
            <Form
              schema={definition.parameters.fields}
              validator={validator}
              onChange={(submitted) => setFieldsValues(submitted.formData)}
              onError={log("errors")}
              liveValidate
              uiSchema={{
                "ui:submitButtonOptions": { norender: true },
              }}
            />
          )}
        </Box>
        <Box mt={2}>
          <Button variant="contained" color="primary" onClick={handleCreate}>
            Create
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

interface ListDefinitionProps {
  onClose: () => void;
  onSelect: (definition: Definition) => void;
}

const ListDefinition = ({ onClose, onSelect }: ListDefinitionProps) => {
  const [availableDefinitions, setAvailableDefinitions] = useState<
    Definition[] | null
  >(null);

  const getAvailableDefinitions = async () => {
    const response = await getDefinitions();
    return response;
  };

  useEffect(() => {
    getAvailableDefinitions().then((response) => {
      setAvailableDefinitions(response as Definition[]);
    });
  }, []);

  return (
    <Box maxHeight='70vh' minWidth='50vw' sx={{ overflowY: 'auto'}}>
      {availableDefinitions == null && <Typography>Loading...</Typography>}
      {availableDefinitions != null && (
        <Stack>
          <Stack>
            {availableDefinitions.map((definition, i) => {
              return (
                // <Button onClick={() => onSelect(definition)}>
                <Box key={`definition-box-${i}`}>
                  <DefinitionBox
                    definition={definition}
                    onClick={() => onSelect(definition)}
                  />
                </Box>
                // </Button>
              );
            })}
          </Stack>
        </Stack>
      )}
    </Box>
  );
};

interface DefinitionBoxProps {
  definition: Definition;
  onClick: () => void;
}

const DefinitionBox = ({ definition, onClick }: DefinitionBoxProps) => {
  const [showMore, setShowMore] = useState(false);
  const spacedLabelValue = (label: string, value: string | number) => {
    return (
      <Box display="flex" justifyContent="space-between">
        <Typography fontSize={14} fontWeight={600}>
          {label}:
        </Typography>
        <Typography fontSize={14}>{value}</Typography>
      </Box>
    );
  };

  return (
    <Card>
      <Box
        sx={{
          mt: 1,
          border: "1px solid black",
          padding: 1.5,
          borderRadius: 2,
        }}
      >
        <CardActionArea onClick={onClick}>
          <Typography fontSize={16} fontWeight={600}>
            {definition.name}
          </Typography>
          {definition.description != null && (
            <Typography fontSize={16}>{definition.description}</Typography>
          )}
          <Box mt={2}>
            {showMore && (
              <Box>
                {spacedLabelValue("Run function", definition.run_function)}
                {spacedLabelValue("Wait time", definition.wait_time)}
                {spacedLabelValue(
                  "Single run",
                  definition.single_run ? "Yes" : "No"
                )}
                {spacedLabelValue("Created by", definition.meta.created_by)}
                {spacedLabelValue(
                  "Input queue",
                  definition.parameters.queues.input_queue?.description ??
                    "None"
                )}
                {spacedLabelValue(
                  "Extra queues",
                  definition.parameters.queues?.extra_queues?.quantity ?? 0
                )}
                {definition.parameters.queues?.extra_queues?.description &&
                  spacedLabelValue(
                    "Extra queues",
                    definition.parameters.queues?.extra_queues?.description ?? 0
                  )}
                {spacedLabelValue(
                  "Output queues",
                  definition.parameters.queues?.output_queues?.quantity ?? 0
                )}
                {definition.parameters.queues?.output_queues?.description &&
                  spacedLabelValue(
                    "Output queues",
                    definition.parameters.queues?.output_queues?.description ??
                      0
                  )}
              </Box>
            )}
          </Box>
        </CardActionArea>
        <Box display="flex" justifyContent="right" alignItems="flex-end">
          {showMore && (
            <IconButton onClick={() => setShowMore(false)} sx={{ fontSize: 5 }}>
              <KeyboardArrowUpIcon />
            </IconButton>
          )}
          {!showMore && (
            <IconButton onClick={() => setShowMore(true)}>
              <KeyboardArrowDownIcon sx={{ fontSize: 20 }} />
            </IconButton>
          )}
        </Box>
      </Box>
    </Card>
  );
};

export default CreateJobModal;
