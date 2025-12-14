/**
 * Client-Side Validations - Unit Tests
 * 
 * Quick test suite to verify validation functions work correctly.
 * Can be run in browser console or Node.js environment.
 */

// Test helper
function runTest(name, testFn) {
  try {
    testFn();
    console.log(`✓ ${name}`);
    return true;
  } catch (error) {
    console.error(`✗ ${name}: ${error.message}`);
    return false;
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertEquals(actual, expected, message) {
  if (actual !== expected) throw new Error(`${message} (expected: ${expected}, got: ${actual})`);
}

function assertArrayEquals(actual, expected, message) {
  if (actual.length !== expected.length) throw new Error(`${message} - length mismatch`);
  for (let i = 0; i < actual.length; i++) {
    if (actual[i] !== expected[i]) throw new Error(`${message} - index ${i} mismatch`);
  }
}

// Run validation tests
console.log('=== Running Validation Tests ===\n');

let passed = 0;
let total = 0;

// Test: parseInputNumbers
console.log('parseInputNumbers Tests:');
total++;
if (runTest('Parse valid comma-separated numbers', () => {
  const result = parseInputNumbers('5, 10, 15');
  assertArrayEquals(result.numbers, [5, 10, 15], 'Numbers array');
  assert(result.isValid === true, 'Should be valid');
})) passed++;

total++;
if (runTest('Parse negative numbers', () => {
  const result = parseInputNumbers('-5, 10, -15');
  assertArrayEquals(result.numbers, [-5, 10, -15], 'Numbers array with negatives');
  assert(result.isValid === true, 'Should be valid');
})) passed++;

total++;
if (runTest('Parse decimal numbers', () => {
  const result = parseInputNumbers('5.5, 10.3, 15.1');
  assert(result.isValid === true, 'Should be valid');
  assert(result.numbers.length === 3, 'Should have 3 numbers');
})) passed++;

total++;
if (runTest('Reject empty string', () => {
  const result = parseInputNumbers('');
  assert(result.isValid === false, 'Should be invalid');
  assert(result.error === ValidationMessages.EMPTY_INPUTS, 'Should return EMPTY_INPUTS error');
})) passed++;

total++;
if (runTest('Reject non-numeric values', () => {
  const result = parseInputNumbers('abc, def');
  assert(result.isValid === false, 'Should be invalid');
})) passed++;

total++;
if (runTest('Handle mixed valid/invalid with warning', () => {
  const result = parseInputNumbers('5, abc, 10');
  assert(result.warning === true, 'Should have warning');
  assertArrayEquals(result.numbers, [5, 10], 'Should extract valid numbers');
})) passed++;

// Test: isValidNumber
console.log('\nisValidNumber Tests:');
total++;
if (runTest('Valid integer', () => {
  assert(isValidNumber(42) === true, '42 is valid');
  assert(isValidNumber('42') === true, '"42" is valid');
})) passed++;

total++;
if (runTest('Valid decimal', () => {
  assert(isValidNumber(3.14) === true, '3.14 is valid');
  assert(isValidNumber('3.14') === true, '"3.14" is valid');
})) passed++;

total++;
if (runTest('Invalid string', () => {
  assert(isValidNumber('abc') === false, '"abc" is invalid');
})) passed++;

total++;
if (runTest('Invalid NaN', () => {
  assert(isValidNumber(NaN) === false, 'NaN is invalid');
  assert(isValidNumber('') === false, 'Empty string is invalid');
})) passed++;

total++;
if (runTest('Invalid Infinity', () => {
  assert(isValidNumber(Infinity) === false, 'Infinity is invalid');
})) passed++;

// Test: isValidOperationType
console.log('\nisValidOperationType Tests:');
total++;
if (runTest('Valid operation types', () => {
  assert(isValidOperationType('addition') === true, 'addition is valid');
  assert(isValidOperationType('subtraction') === true, 'subtraction is valid');
  assert(isValidOperationType('multiplication') === true, 'multiplication is valid');
  assert(isValidOperationType('division') === true, 'division is valid');
})) passed++;

total++;
if (runTest('Case insensitive validation', () => {
  assert(isValidOperationType('ADDITION') === true, 'ADDITION is valid');
  assert(isValidOperationType('Addition') === true, 'Addition is valid');
})) passed++;

total++;
if (runTest('Invalid operation types', () => {
  assert(isValidOperationType('modulo') === false, 'modulo is invalid');
  assert(isValidOperationType('') === false, 'empty string is invalid');
})) passed++;

// Test: validateCalculationInputs
console.log('\nvalidateCalculationInputs Tests:');
total++;
if (runTest('Valid addition', () => {
  const result = validateCalculationInputs('addition', '5, 10, 15');
  assert(result.isValid === true, 'Should be valid');
  assertEquals(result.data.type, 'addition', 'Type should be addition');
  assertArrayEquals(result.data.inputs, [5, 10, 15], 'Inputs should match');
})) passed++;

total++;
if (runTest('Invalid: empty inputs', () => {
  const result = validateCalculationInputs('addition', '');
  assert(result.isValid === false, 'Should be invalid');
  assert(result.errors.length > 0, 'Should have errors');
})) passed++;

total++;
if (runTest('Invalid: only one number', () => {
  const result = validateCalculationInputs('addition', '5');
  assert(result.isValid === false, 'Should be invalid');
})) passed++;

total++;
if (runTest('Invalid: division by zero', () => {
  const result = validateCalculationInputs('division', '100, 0');
  assert(result.isValid === false, 'Should be invalid');
  assert(result.errors.some(e => e.includes('zero')), 'Should mention zero');
})) passed++;

total++;
if (runTest('Valid: division with non-zero divisor', () => {
  const result = validateCalculationInputs('division', '100, 2, 5');
  assert(result.isValid === true, 'Should be valid');
})) passed++;

total++;
if (runTest('Invalid: invalid operation type', () => {
  const result = validateCalculationInputs('modulo', '5, 10');
  assert(result.isValid === false, 'Should be invalid');
})) passed++;

// Test: calculateResult
console.log('\ncalculateResult Tests:');
total++;
if (runTest('Addition', () => {
  const result = calculateResult('addition', [5, 10, 15]);
  assertEquals(result, 30, 'Addition result');
})) passed++;

total++;
if (runTest('Subtraction', () => {
  const result = calculateResult('subtraction', [100, 30, 10]);
  assertEquals(result, 60, 'Subtraction result: 100 - 30 - 10');
})) passed++;

total++;
if (runTest('Multiplication', () => {
  const result = calculateResult('multiplication', [2, 3, 4]);
  assertEquals(result, 24, 'Multiplication result');
})) passed++;

total++;
if (runTest('Division', () => {
  const result = calculateResult('division', [100, 2, 5]);
  assertEquals(result, 10, 'Division result: 100 / 2 / 5');
})) passed++;

total++;
if (runTest('Division by zero returns error', () => {
  const result = calculateResult('division', [100, 0]);
  assert(typeof result === 'string' && result.includes('zero'), 'Should return error message');
})) passed++;

// Test: formatNumber
console.log('\nformatNumber Tests:');
total++;
if (runTest('Format integer', () => {
  const result = formatNumber(42);
  assertEquals(result, 42, 'Integer formatted');
})) passed++;

total++;
if (runTest('Format decimal with rounding', () => {
  const result = formatNumber(3.14159265);
  // Should round to 4 decimal places
  assert(result === 3.1416, 'Should round to 4 decimals');
})) passed++;

total++;
if (runTest('Format very small number with exponential', () => {
  const result = formatNumber(0.00001);
  assert(typeof result === 'string' && result.includes('e'), 'Should use exponential notation');
})) passed++;

// Test: getOperatorSymbol
console.log('\ngetOperatorSymbol Tests:');
total++;
if (runTest('Get correct operators', () => {
  assertEquals(getOperatorSymbol('addition'), '+', 'Addition operator');
  assertEquals(getOperatorSymbol('subtraction'), '-', 'Subtraction operator');
  assertEquals(getOperatorSymbol('multiplication'), '×', 'Multiplication operator');
  assertEquals(getOperatorSymbol('division'), '÷', 'Division operator');
})) passed++;

// Test: validateInputField
console.log('\nvalidateInputField Tests:');
total++;
if (runTest('Real-time validation with warning', () => {
  const mockInput = { value: '5' };
  const result = validateInputField(mockInput);
  assert(result.warnings.length > 0, 'Should have warnings for single number');
})) passed++;

// Summary
console.log('\n=== Test Summary ===');
console.log(`Passed: ${passed}/${total}`);
console.log(`Failed: ${total - passed}/${total}`);
console.log(`Success Rate: ${((passed/total)*100).toFixed(1)}%`);

if (passed === total) {
  console.log('\n✓ All tests passed!');
} else {
  console.log(`\n✗ ${total - passed} test(s) failed`);
}
