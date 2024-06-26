import { TDraggableEvent } from "./draggable-event";

export type TDraggableEventWithReason = {event: TDraggableEvent; reason: 'start' | 'end' | 'move' | 'cancel' };
