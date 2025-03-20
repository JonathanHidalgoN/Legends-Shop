export interface ValidationResult {
  valid: boolean,
  input: string | null,
  msg: string | null
}

export const defaultValidationResult: ValidationResult = {
  valid: true,
  input: null,
  msg: null,
};
