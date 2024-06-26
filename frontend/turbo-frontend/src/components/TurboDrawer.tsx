import {
  Box,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Stack,
} from "@mui/material";
import Drawer from "@mui/material/Drawer";
import ColorModeToggle from "./ColorModeToggle";

interface Props {
  open: boolean;
  handleDrawerClose: () => void;
}

export default function TurboDrawer({ open, handleDrawerClose }: Props) {
  return (
    <Drawer open={open} anchor="left" onClose={handleDrawerClose}>
      <Stack height='100%' flexDirection='column-reverse' >
        <List>
          <ListItem>
            <ColorModeToggle />
          </ListItem>
        </List>
      </Stack>
    </Drawer>
  );
}
