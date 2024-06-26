import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { Button, Link, Menu, MenuItem, Stack } from "@mui/material";
import { listJobGroup } from "../api/turbo-api";
import { useState } from "react";

interface Props {
  groupPath: string;
  handleGoToGroup: (path: string) => void;
}

export default function TurboLowBar({ groupPath, handleGoToGroup }: Props) {
  const [subGroupMapping, setSubGroupMapping] = useState<
    Record<string, string[]>
  >({});

  const handleListSubgroups = async (path: string) => {
    if (!subGroupMapping[path]) {
      const result = await listJobGroup(path);
      setSubGroupMapping((prev) => ({ ...prev, [path]: result }));
      return result;
    }
    return subGroupMapping[path];
  };

  return (
    <Box sx={{ border: "1px solid #000" }}>
      <Stack py={1} pl={5} direction="row">
        <Typography display="inline" whiteSpace="pre">
          Path:{" "}
        </Typography>
        <PathLinks
          path={groupPath}
          handleListSubgroups={handleListSubgroups}
          handleGoToGroup={handleGoToGroup}
        />
      </Stack>
    </Box>
  );
}

interface PathLinksProps {
  path: string;
  handleListSubgroups: (path: string) => Promise<string[]>;
  handleGoToGroup: (path: string) => void;
}

function PathLinks({
  path,
  handleListSubgroups,
  handleGoToGroup,
}: PathLinksProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [subgroups, setSubgroups] = useState<string[]>([]);

  const handleClick = async (
    event: React.MouseEvent<HTMLButtonElement>,
    subgroupPath: string[]
  ) => {
    setAnchorEl(event.currentTarget);
    const subgroups = await handleListSubgroups(subgroupPath.join("/"));
    setSubgroups(subgroups);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleGoToGroupClick = (path: string) => {
    handleGoToGroup(path);
    setAnchorEl(null);
    handleClose();
  };

  const pathParts = path.split("/");

  const getGroupsLink = (part: string, index: number) => {
    const subgroupPath = pathParts.slice(0, index);

    return (
      <Box>
        <Box
          m={0}
          px={1}
          py={0}
          component={Button}
          sx={{
            textTransform: "none",
          }}
          disableRipple
          disableElevation
          disableFocusRipple
          disableTouchRipple
          onClick={(event) => handleClick(event, subgroupPath)}
        >
          <Link
            key={index}
            style={{ cursor: "pointer" }}
            sx={{ color: "black" }}
          >
            <Typography display="inline" fontWeight={700}>
              {part}
            </Typography>
          </Link>
        </Box>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleClose}
          anchorOrigin={{
            vertical: "top",
            horizontal: "left",
          }}
          transformOrigin={{
            vertical: "bottom",
            horizontal: "left",
          }}
        >
          {subgroups &&
            subgroups.map((subgroup) => {
              const completeSubgropuPath = [...subgroupPath, subgroup].join(
                "/"
              );
              return (
                <MenuItem
                  style={{ cursor: "pointer" }}
                  onClick={() => handleGoToGroupClick(completeSubgropuPath)}
                  key={completeSubgropuPath}
                  disableRipple
                  disableTouchRipple
                >
                  {subgroup}
                </MenuItem>
              );
            })}
        </Menu>
      </Box>
    );
  };

  return (
    <>
      {pathParts &&
        pathParts.map((part, index) => (
          <Box key={part}>
            {getGroupsLink(part, index)}
            {index < pathParts.length - 1 && (
              <Typography display="inline" whiteSpace="pre">
                {" / "}
              </Typography>
            )}
          </Box>
        ))}
    </>
  );
}
