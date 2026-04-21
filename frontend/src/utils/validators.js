/**
 * Validators für Vue Component Props
 */

// Task Validator
export const taskValidator = (obj) => {
  if (!obj || typeof obj !== 'object') return false;
  return (
    typeof obj.id === 'number' &&
    typeof obj.title === 'string' &&
    typeof obj.status === 'string' &&
    ['OPEN', 'IN_PROGRESS', 'REVIEW', 'DONE'].includes(obj.status)
  );
};

// Project Validator
export const projectValidator = (obj) => {
  if (!obj || typeof obj !== 'object') return false;
  return (
    typeof obj.id === 'number' &&
    typeof obj.title === 'string' &&
    (obj.due_date === null || typeof obj.due_date === 'string')
  );
};

// User/Profile Validator
export const userValidator = (obj) => {
  if (!obj || typeof obj !== 'object') return false;
  return (
    typeof obj.id === 'number' &&
    typeof obj.name === 'string' &&
    typeof obj.email === 'string'
  );
};

// Array of Tasks Validator
export const tasksArrayValidator = (arr) => {
  if (!Array.isArray(arr)) return false;
  return arr.every(taskValidator);
};

// Array of Users Validator
export const usersArrayValidator = (arr) => {
  if (!Array.isArray(arr)) return false;
  return arr.every(userValidator);
};

// Generic ID Validator
export const idValidator = (val) => {
  return typeof val === 'number' && val > 0;
};

// Status Validator
export const statusValidator = (val) => {
  const validStatuses = ['OPEN', 'IN_PROGRESS', 'REVIEW', 'DONE'];
  return validStatuses.includes(val);
};

// Priority Validator
export const priorityValidator = (val) => {
  const validPriorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
  return validPriorities.includes(val);
};

// Helper: Generate Error Message
export const generateValidationError = (propName, expectedType, receivedValue) => {
  return `[Props Validation] ${propName}: Expected ${expectedType}, got ${typeof receivedValue} (${JSON.stringify(receivedValue).slice(0, 50)})`;
};
