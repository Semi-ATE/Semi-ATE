export interface MultichoiceEntry {
  checked: boolean;
  backgroundColor: string;
  textColor: string;
  label: string;
}

export interface MultichoiceConfiguration {
  readonly: boolean;
  items: Array<MultichoiceEntry>;
  label: string;
}

export function initMultichoiceEntry(label: string, checked: boolean = false, backgroundColor: string = 'white', textColor: string = 'black'): MultichoiceEntry {
  return {
    checked,
    label,
    textColor,
    backgroundColor
  };
}