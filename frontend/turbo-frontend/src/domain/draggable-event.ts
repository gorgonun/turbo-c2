import { DragCancelEvent, DragEndEvent, DragMoveEvent, DragStartEvent } from "@dnd-kit/core";

export type TDraggableEvent = DragStartEvent | DragEndEvent | DragMoveEvent | DragCancelEvent;
