import { RefObject } from "react";

// source: https://stackoverflow.com/questions/32553158/detect-click-outside-react-component
export function handleClickOutside(
  event: MouseEvent,
  ref: RefObject<HTMLDivElement | null>,
  noShowSetFunction: (value: boolean) => void,
) {
  if (ref.current && !ref.current.contains(event.target as Node)) {
    noShowSetFunction(false);
  }
}
