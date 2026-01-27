import React from 'react';
import type { Kit } from '../types/kit';

interface WarningBadgeProps {
  kit: Kit;
}

/**
 * Warning badge component for displaying soft warnings on kits.
 * 
 * Implements CUSTODY-008 and CUSTODY-014:
 * - Shows overdue return warnings
 * - Shows extended custody warnings
 * - Non-blocking visual indicators
 */
const WarningBadge: React.FC<WarningBadgeProps> = ({ kit }) => {
  if (!kit.has_warning) {
    return null;
  }

  // Determine warning severity and message
  let warningColor = 'bg-yellow-100 text-yellow-800 border-yellow-300';
  let warningIcon = '⚠️';
  let warningText = '';

  if (kit.overdue_return && kit.days_overdue) {
    // Overdue is more critical
    warningColor = 'bg-red-100 text-red-800 border-red-300';
    warningIcon = '🔴';
    warningText = `Overdue ${kit.days_overdue} day${kit.days_overdue > 1 ? 's' : ''}`;
  } else if (kit.extended_custody && kit.days_checked_out) {
    // Extended custody is less critical
    warningColor = 'bg-orange-100 text-orange-800 border-orange-300';
    warningIcon = '⏰';
    warningText = `Out ${kit.days_checked_out} days`;
  }

  return (
    <div className={`px-2 py-1 rounded text-xs font-semibold border ${warningColor} flex items-center gap-1`}>
      <span>{warningIcon}</span>
      <span>{warningText}</span>
    </div>
  );
};

export default WarningBadge;
