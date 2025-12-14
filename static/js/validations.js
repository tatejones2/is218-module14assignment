/**
 * Client-side Validation Module
 * 
 * This module provides comprehensive validation functions for the calculator application.
 * All validations are performed before sending data to the backend API.
 */

// Validation error messages
const ValidationMessages = {
  EMPTY_FIELD: 'This field is required',
  INVALID_NUMBER: 'Please enter a valid number',
  INVALID_OPERATION: 'Please select a valid operation type',
  INSUFFICIENT_INPUTS: 'At least two numbers are required for a calculation',
  DIVISION_BY_ZERO: 'Cannot divide by zero',
  EMPTY_INPUTS: 'Please enter at least two numbers separated by commas',
  INVALID_INPUT_FORMAT: 'Invalid input format. Please use comma-separated numbers',
  NO_VALID_NUMBERS: 'No valid numbers found in the input'
};

const VALID_OPERATION_TYPES = ['addition', 'subtraction', 'multiplication', 'division'];

/**
 * Validates that a value is a valid number
 * @param {*} value - The value to validate
 * @returns {boolean} True if the value is a valid number
 */
function isValidNumber(value) {
  const num = parseFloat(value);
  return !isNaN(num) && isFinite(num);
}

/**
 * Validates that the operation type is valid
 * @param {string} type - The operation type to validate
 * @returns {boolean} True if the type is valid
 */
function isValidOperationType(type) {
  return VALID_OPERATION_TYPES.includes(type?.toLowerCase());
}

/**
 * Parses a comma-separated string of numbers into an array
 * @param {string} inputString - Comma-separated numbers
 * @returns {object} Object with { numbers: number[], isValid: boolean, error?: string }
 */
function parseInputNumbers(inputString) {
  if (!inputString || typeof inputString !== 'string') {
    return { numbers: [], isValid: false, error: ValidationMessages.EMPTY_INPUTS };
  }

  // Split by comma and trim whitespace
  const parts = inputString.split(',').map(s => s.trim()).filter(s => s.length > 0);

  if (parts.length === 0) {
    return { numbers: [], isValid: false, error: ValidationMessages.EMPTY_INPUTS };
  }

  // Convert to numbers and validate each one
  const numbers = [];
  const invalidParts = [];

  parts.forEach((part, index) => {
    if (isValidNumber(part)) {
      numbers.push(parseFloat(part));
    } else {
      invalidParts.push(part);
    }
  });

  if (numbers.length === 0) {
    return { numbers: [], isValid: false, error: ValidationMessages.INVALID_INPUT_FORMAT };
  }

  if (invalidParts.length > 0) {
    return { 
      numbers, 
      isValid: false, 
      error: `Invalid numbers detected: ${invalidParts.join(', ')}. These will be ignored.`,
      warning: true 
    };
  }

  return { numbers, isValid: true };
}

/**
 * Validates calculation inputs
 * @param {string} operationType - The type of operation
 * @param {string} inputsString - Comma-separated input numbers
 * @returns {object} Validation result object
 */
function validateCalculationInputs(operationType, inputsString) {
  const result = {
    isValid: true,
    errors: [],
    warnings: [],
    data: null
  };

  // Validate operation type
  if (!operationType) {
    result.errors.push('Operation type is required');
    result.isValid = false;
  } else if (!isValidOperationType(operationType)) {
    result.errors.push(ValidationMessages.INVALID_OPERATION);
    result.isValid = false;
  }

  // Parse and validate input numbers
  const parseResult = parseInputNumbers(inputsString);

  if (!parseResult.isValid) {
    result.errors.push(parseResult.error);
    result.isValid = false;
  } else {
    if (parseResult.warning) {
      result.warnings.push(parseResult.error);
    }

    // Check if we have at least 2 numbers
    if (parseResult.numbers.length < 2) {
      result.errors.push(ValidationMessages.INSUFFICIENT_INPUTS);
      result.isValid = false;
    } else {
      // Check for division by zero (applies only to division operation)
      if (operationType?.toLowerCase() === 'division') {
        const divisors = parseResult.numbers.slice(1);
        if (divisors.some(num => num === 0)) {
          result.errors.push(ValidationMessages.DIVISION_BY_ZERO);
          result.isValid = false;
        }
      }

      // If all validations pass, store the parsed data
      if (result.isValid) {
        result.data = {
          type: operationType.toLowerCase(),
          inputs: parseResult.numbers
        };
      }
    }
  }

  return result;
}

/**
 * Performs real-time input validation on the inputs field
 * @param {HTMLElement} inputElement - The input field element
 * @returns {object} Validation result
 */
function validateInputField(inputElement) {
  const value = inputElement.value.trim();
  const result = {
    isValid: true,
    errors: [],
    warnings: []
  };

  if (value === '') {
    result.isValid = true; // Empty is OK for real-time validation
    return result;
  }

  const parseResult = parseInputNumbers(value);

  if (!parseResult.isValid) {
    result.isValid = false;
    result.errors.push(parseResult.error);
  } else {
    if (parseResult.warning) {
      result.warnings.push(parseResult.error);
    }

    // Real-time warning for less than 2 numbers
    if (parseResult.numbers.length < 2) {
      result.warnings.push(`${parseResult.numbers.length} number(s) found. At least 2 are required.`);
    }
  }

  return result;
}

/**
 * Adds visual feedback to an input element based on validation status
 * @param {HTMLElement} inputElement - The input field
 * @param {string} status - 'valid', 'invalid', or 'warning'
 */
function setInputFieldStatus(inputElement, status = null) {
  // Remove all status classes
  inputElement.classList.remove('border-red-500', 'border-yellow-500', 'border-green-500', 'bg-red-50', 'bg-yellow-50', 'bg-green-50');

  if (status === 'invalid') {
    inputElement.classList.add('border-red-500', 'bg-red-50');
  } else if (status === 'warning') {
    inputElement.classList.add('border-yellow-500', 'bg-yellow-50');
  } else if (status === 'valid') {
    inputElement.classList.add('border-green-500', 'bg-green-50');
  }
}

/**
 * Creates a formatted error/warning message display
 * @param {string[]} errors - Array of error messages
 * @param {string[]} warnings - Array of warning messages
 * @returns {string} HTML string for display
 */
function createValidationMessageHTML(errors, warnings) {
  let html = '';

  if (errors.length > 0) {
    html += '<div class="mt-2 text-sm text-red-700">';
    errors.forEach(error => {
      html += `<div class="flex items-start"><span class="mr-2">•</span><span>${error}</span></div>`;
    });
    html += '</div>';
  }

  if (warnings.length > 0) {
    html += '<div class="mt-2 text-sm text-yellow-700">';
    warnings.forEach(warning => {
      html += `<div class="flex items-start"><span class="mr-2">⚠</span><span>${warning}</span></div>`;
    });
    html += '</div>';
  }

  return html;
}

/**
 * Clears validation messages from a container
 * @param {HTMLElement} container - The container to clear messages from
 */
function clearValidationMessages(container) {
  const messageElements = container.querySelectorAll('[data-validation-message]');
  messageElements.forEach(el => el.remove());
}

/**
 * Calculates the result of a calculation for preview purposes
 * @param {string} type - The operation type
 * @param {number[]} inputs - Array of input numbers
 * @returns {number|string} The calculated result or error message
 */
function calculateResult(type, inputs) {
  if (!inputs || inputs.length < 2) {
    return null;
  }

  try {
    switch (type?.toLowerCase()) {
      case 'addition':
        return inputs.reduce((a, b) => a + b, 0);
      case 'subtraction':
        return inputs.reduce((a, b, i) => i === 0 ? a : a - b, inputs[0]);
      case 'multiplication':
        return inputs.reduce((a, b) => a * b, 1);
      case 'division':
        // Check for division by zero
        if (inputs.some((value, index) => index > 0 && value === 0)) {
          return 'Cannot divide by zero';
        }
        return inputs.reduce((a, b, i) => i === 0 ? a : a / b, inputs[0]);
      default:
        return 'Unknown operation';
    }
  } catch (error) {
    return `Error: ${error.message}`;
  }
}

/**
 * Formats a number for display
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
  if (typeof num !== 'number') return String(num);

  // Use exponential notation for very small numbers
  if (Math.abs(num) < 0.0001 && num !== 0) {
    return num.toExponential(4);
  }

  // Round to 4 decimal places for display
  return Math.round(num * 10000) / 10000;
}

/**
 * Gets the operation symbol for display
 * @param {string} type - The operation type
 * @returns {string} The operator symbol
 */
function getOperatorSymbol(type) {
  const symbols = {
    'addition': '+',
    'subtraction': '-',
    'multiplication': '×',
    'division': '÷'
  };
  return symbols[type?.toLowerCase()] || '?';
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    validateCalculationInputs,
    validateInputField,
    parseInputNumbers,
    isValidNumber,
    isValidOperationType,
    setInputFieldStatus,
    createValidationMessageHTML,
    clearValidationMessages,
    calculateResult,
    formatNumber,
    getOperatorSymbol,
    ValidationMessages,
    VALID_OPERATION_TYPES
  };
}
