/**
 * Frontend Validation - Usage Examples
 * 
 * This file demonstrates how to use the validation module in your application.
 */

// ============================================================================
// EXAMPLE 1: Form Submission Validation
// ============================================================================

/**
 * Validate form before submission to the API
 */
function handleFormSubmit(event) {
  event.preventDefault();
  
  // Get form values
  const operationType = document.getElementById('calcType').value;
  const inputsString = document.getElementById('calcInputs').value;
  
  // Validate using the module
  const validationResult = validateCalculationInputs(operationType, inputsString);
  
  if (!validationResult.isValid) {
    // Show errors
    console.error('Validation errors:', validationResult.errors);
    
    // Highlight the input field
    setInputFieldStatus(document.getElementById('calcInputs'), 'invalid');
    
    // Display error messages to user
    const errorHTML = createValidationMessageHTML(
      validationResult.errors, 
      validationResult.warnings
    );
    document.getElementById('errorMessages').innerHTML = errorHTML;
    
    return;
  }
  
  // If valid, use the parsed data
  const calculationData = validationResult.data;
  
  // Send to API
  fetch('/calculations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(calculationData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Calculation created:', data);
    // Show success feedback
  })
  .catch(error => console.error('API Error:', error));
}

// ============================================================================
// EXAMPLE 2: Real-Time Input Validation
// ============================================================================

/**
 * Add real-time validation feedback as user types
 */
function setupRealtimeValidation(inputElement) {
  inputElement.addEventListener('input', function() {
    // Validate the input field
    const validationResult = validateInputField(this);
    
    // Determine status based on validation result
    let status = null;
    if (this.value.trim() === '') {
      status = null; // Empty = no feedback
    } else if (!validationResult.isValid) {
      status = 'invalid';
    } else if (validationResult.warnings.length > 0) {
      status = 'warning';
    } else {
      status = 'valid';
    }
    
    // Apply visual feedback
    setInputFieldStatus(this, status);
    
    // Display validation messages
    const messageHTML = createValidationMessageHTML(
      validationResult.errors,
      validationResult.warnings
    );
    document.getElementById('validationMessages').innerHTML = messageHTML;
  });
}

// Usage:
// setupRealtimeValidation(document.getElementById('calcInputs'));

// ============================================================================
// EXAMPLE 3: Live Preview Calculation
// ============================================================================

/**
 * Show a live preview of the calculation result as user types
 */
function setupLivePreview(typeElement, inputsElement, previewElement) {
  const updatePreview = () => {
    const type = typeElement.value;
    const inputsString = inputsElement.value;
    
    // Parse the inputs
    const parseResult = parseInputNumbers(inputsString);
    
    if (parseResult.isValid && parseResult.numbers.length >= 2) {
      // Calculate the result
      const result = calculateResult(type, parseResult.numbers);
      
      // Format for display
      const formattedResult = formatNumber(result);
      const operator = getOperatorSymbol(type);
      
      // Create visual representation
      const html = `
        <div class="calculation-preview">
          <div class="formula">
            ${parseResult.numbers.map((num, i) => `
              <span class="number">${num}</span>
              ${i < parseResult.numbers.length - 1 ? `<span class="operator">${operator}</span>` : ''}
            `).join('')}
          </div>
          <div class="equals">=</div>
          <div class="result">${formattedResult}</div>
        </div>
      `;
      
      previewElement.innerHTML = html;
    } else {
      previewElement.innerHTML = '<p>Enter valid inputs to see preview</p>';
    }
  };
  
  // Update on input change
  typeElement.addEventListener('change', updatePreview);
  inputsElement.addEventListener('input', updatePreview);
}

// Usage:
// setupLivePreview(
//   document.getElementById('calcType'),
//   document.getElementById('calcInputs'),
//   document.getElementById('preview')
// );

// ============================================================================
// EXAMPLE 4: Individual Input Validation
// ============================================================================

/**
 * Validate a single input field
 */
function validateSingleInput(inputString) {
  const parseResult = parseInputNumbers(inputString);
  
  if (!parseResult.isValid) {
    console.error('Invalid input:', parseResult.error);
    return null;
  }
  
  if (parseResult.warning) {
    console.warn('Input warning:', parseResult.error);
  }
  
  return parseResult.numbers;
}

// Usage:
// const numbers = validateSingleInput('5, 10, 15');
// console.log(numbers); // [5, 10, 15]

// ============================================================================
// EXAMPLE 5: Operation Type Validation
// ============================================================================

/**
 * Validate operation type
 */
function validateOperation(type) {
  if (!isValidOperationType(type)) {
    console.error(`Invalid operation type: ${type}`);
    console.log(`Valid types: ${VALID_OPERATION_TYPES.join(', ')}`);
    return null;
  }
  
  return type.toLowerCase();
}

// Usage:
// const op = validateOperation('addition'); // 'addition'
// const op = validateOperation('DIVISION'); // 'division'
// const op = validateOperation('modulo');   // null

// ============================================================================
// EXAMPLE 6: Custom Validation with Error Display
// ============================================================================

/**
 * Comprehensive validation with custom error handling
 */
function validateAndDisplayErrors(type, inputs) {
  // Get validation result
  const result = validateCalculationInputs(type, inputs);
  
  // Create error container if not exists
  let errorContainer = document.getElementById('customErrors');
  if (!errorContainer) {
    errorContainer = document.createElement('div');
    errorContainer.id = 'customErrors';
    document.body.appendChild(errorContainer);
  }
  
  if (result.isValid) {
    // Clear errors and show success
    errorContainer.innerHTML = '<div class="success">✓ Validation passed!</div>';
    errorContainer.style.color = 'green';
    return result.data;
  }
  
  // Show errors
  const html = createValidationMessageHTML(result.errors, result.warnings);
  errorContainer.innerHTML = html;
  errorContainer.style.color = 'red';
  
  return null;
}

// ============================================================================
// EXAMPLE 7: Batch Validation
// ============================================================================

/**
 * Validate multiple calculations at once
 */
function validateMultipleCalculations(calculations) {
  const results = calculations.map(calc => {
    const validation = validateCalculationInputs(calc.type, calc.inputs.join(', '));
    return {
      original: calc,
      validation: validation,
      isValid: validation.isValid
    };
  });
  
  // Separate valid and invalid
  const valid = results.filter(r => r.isValid);
  const invalid = results.filter(r => !r.isValid);
  
  return { valid, invalid, results };
}

// Usage:
// const calcs = [
//   { type: 'addition', inputs: [1, 2, 3] },
//   { type: 'division', inputs: [10, 0] }
// ];
// const { valid, invalid } = validateMultipleCalculations(calcs);

// ============================================================================
// EXAMPLE 8: Number Formatting Utilities
// ============================================================================

/**
 * Format numbers for different purposes
 */
function demonstrateFormatting() {
  console.log(formatNumber(42));           // 42
  console.log(formatNumber(3.14159));      // 3.1416
  console.log(formatNumber(0.00001));      // 1e-5
  console.log(formatNumber(1234567.89));   // 1234567.89
  console.log(formatNumber(-3.14));        // -3.14
}

// ============================================================================
// EXAMPLE 9: Operator Symbol Display
// ============================================================================

/**
 * Get symbols for visual display
 */
function demonstrateOperators() {
  const operators = {
    addition: getOperatorSymbol('addition'),           // +
    subtraction: getOperatorSymbol('subtraction'),     // -
    multiplication: getOperatorSymbol('multiplication'),// ×
    division: getOperatorSymbol('division')            // ÷
  };
  
  console.log(operators);
}

// ============================================================================
// EXAMPLE 10: Advanced Error Handling
// ============================================================================

/**
 * Advanced error handling with recovery suggestions
 */
function validateWithSuggestions(type, inputs) {
  const result = validateCalculationInputs(type, inputs);
  
  if (result.isValid) {
    return { isValid: true, data: result.data };
  }
  
  // Provide helpful suggestions
  const suggestions = [];
  
  if (result.errors.some(e => e.includes('numbers'))) {
    suggestions.push('Tip: Use at least 2 numbers separated by commas (e.g., "5, 10, 15")');
  }
  
  if (result.errors.some(e => e.includes('operation'))) {
    suggestions.push(`Tip: Choose from: ${VALID_OPERATION_TYPES.join(', ')}`);
  }
  
  if (result.errors.some(e => e.includes('zero'))) {
    suggestions.push('Tip: Division by zero is not allowed. Use non-zero divisors.');
  }
  
  if (result.errors.some(e => e.includes('format'))) {
    suggestions.push('Tip: Invalid format. Try "5, 10, 15" for addition');
  }
  
  return {
    isValid: false,
    errors: result.errors,
    warnings: result.warnings,
    suggestions: suggestions
  };
}

// Usage:
// const validation = validateWithSuggestions('division', '100, 0');
// console.log(validation.suggestions); // Display helpful tips

// ============================================================================
// EXAMPLE 11: Complete Form Integration
// ============================================================================

/**
 * Complete form setup with all validation features
 */
function setupCalculationForm() {
  const form = document.getElementById('calculationForm');
  const typeSelect = document.getElementById('calcType');
  const inputsInput = document.getElementById('calcInputs');
  const previewDiv = document.getElementById('preview');
  const messagesDiv = document.getElementById('messages');
  
  // Setup real-time validation
  setupRealtimeValidation(inputsInput);
  
  // Setup live preview
  setupLivePreview(typeSelect, inputsInput, previewDiv);
  
  // Setup form submission
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // Validate
    const validation = validateCalculationInputs(
      typeSelect.value,
      inputsInput.value
    );
    
    if (!validation.isValid) {
      // Show errors
      const html = createValidationMessageHTML(
        validation.errors,
        validation.warnings
      );
      messagesDiv.innerHTML = html;
      messagesDiv.className = 'error-messages';
      return;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';
    
    try {
      // Send to API
      const response = await fetch('/calculations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(validation.data)
      });
      
      const result = await response.json();
      
      // Show success
      messagesDiv.innerHTML = `
        <div class="success">
          ✓ Calculation created! Result: ${formatNumber(result.result)}
        </div>
      `;
      messagesDiv.className = 'success-messages';
      
      // Reset form
      form.reset();
      previewDiv.innerHTML = '';
      
    } catch (error) {
      // Show error
      messagesDiv.innerHTML = `<div class="error">✗ Error: ${error.message}</div>`;
      messagesDiv.className = 'error-messages';
    } finally {
      // Restore button
      submitBtn.disabled = false;
      submitBtn.textContent = 'Calculate';
    }
  });
}

// Call on page load:
// document.addEventListener('DOMContentLoaded', setupCalculationForm);

// ============================================================================
// EXAMPLE 12: Validation Constants Reference
// ============================================================================

/**
 * Available validation constants
 */
function showValidationConstants() {
  console.log('=== Validation Constants ===');
  console.log('Valid Operations:', VALID_OPERATION_TYPES);
  // Output: ['addition', 'subtraction', 'multiplication', 'division']
  
  console.log('Error Messages:');
  Object.entries(ValidationMessages).forEach(([key, msg]) => {
    console.log(`  ${key}: "${msg}"`);
  });
}

// ============================================================================
