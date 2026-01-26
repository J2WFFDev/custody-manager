// Helper utility functions will be added here
// Example: date formatting, validation, constants

/**
 * Get Tailwind CSS classes for role badge colors
 */
export const getRoleBadgeColor = (role: string): string => {
  const colors: { [key: string]: string } = {
    admin: 'bg-purple-100 text-purple-800',
    armorer: 'bg-blue-100 text-blue-800',
    coach: 'bg-green-100 text-green-800',
    volunteer: 'bg-yellow-100 text-yellow-800',
    parent: 'bg-gray-100 text-gray-800'
  };
  return colors[role] || 'bg-gray-100 text-gray-800';
};
