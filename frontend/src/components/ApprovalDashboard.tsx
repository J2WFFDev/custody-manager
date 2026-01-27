import React, { useState, useEffect } from 'react';
import { custodyService } from '../services/custodyService';
import type { ApprovalRequest, ApprovalDecisionResponse } from '../types/custody';

const ApprovalDashboard: React.FC = () => {
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [denialReason, setDenialReason] = useState<string>('');
  const [showDenialModal, setShowDenialModal] = useState<number | null>(null);

  const loadPendingApprovals = async () => {
    try {
      setLoading(true);
      setError(null);
      const approvals = await custodyService.getPendingApprovals();
      setPendingApprovals(approvals);
    } catch (err) {
      console.error('Failed to load pending approvals:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load pending approvals. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPendingApprovals();
  }, []);

  const handleApprove = async (approvalId: number) => {
    try {
      setProcessingId(approvalId);
      setError(null);
      
      const response: ApprovalDecisionResponse = await custodyService.approveOrDenyOffSite({
        approval_request_id: approvalId,
        approve: true
      });
      
      // Remove from pending list
      setPendingApprovals(prev => prev.filter(a => a.id !== approvalId));
      
      // Show success message
      alert(response.message);
    } catch (err) {
      console.error('Failed to approve request:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to approve request. Please try again.');
      }
    } finally {
      setProcessingId(null);
    }
  };

  const handleDenyClick = (approvalId: number) => {
    setShowDenialModal(approvalId);
    setDenialReason('');
  };

  const handleDenyConfirm = async () => {
    if (!showDenialModal) return;
    
    if (!denialReason.trim()) {
      alert('Please provide a reason for denial.');
      return;
    }

    try {
      setProcessingId(showDenialModal);
      setError(null);
      
      const response: ApprovalDecisionResponse = await custodyService.approveOrDenyOffSite({
        approval_request_id: showDenialModal,
        approve: false,
        denial_reason: denialReason.trim()
      });
      
      // Remove from pending list
      setPendingApprovals(prev => prev.filter(a => a.id !== showDenialModal));
      
      // Close modal and show success
      setShowDenialModal(null);
      setDenialReason('');
      alert(response.message);
    } catch (err) {
      console.error('Failed to deny request:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to deny request. Please try again.');
      }
    } finally {
      setProcessingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Off-Site Checkout Approvals</h1>
        <p className="text-gray-600 mt-2">Review and approve off-site checkout requests</p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {pendingApprovals.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Approvals</h3>
          <p className="text-gray-600">There are currently no off-site checkout requests awaiting approval.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingApprovals.map((approval) => (
            <div key={approval.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="text-xl font-semibold text-gray-800">
                      {approval.kit_name} ({approval.kit_code})
                    </h3>
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">
                      Pending
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Requested By</p>
                      <p className="font-medium text-gray-800">{approval.requester_name}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Custodian (Taking Off-Site)</p>
                      <p className="font-medium text-gray-800">{approval.custodian_name}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Requested At</p>
                      <p className="font-medium text-gray-800">{formatDate(approval.created_at)}</p>
                    </div>
                    
                    {approval.notes && (
                      <div className="md:col-span-2">
                        <p className="text-sm text-gray-600 mb-1">Notes</p>
                        <p className="text-gray-800">{approval.notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex gap-3 mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleApprove(approval.id)}
                  disabled={processingId === approval.id}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {processingId === approval.id ? 'Processing...' : 'Approve'}
                </button>
                
                <button
                  onClick={() => handleDenyClick(approval.id)}
                  disabled={processingId === approval.id}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Deny
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Denial Modal */}
      {showDenialModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Deny Off-Site Checkout</h3>
            
            <div className="mb-4">
              <label htmlFor="denialReason" className="block text-sm font-medium text-gray-700 mb-2">
                Reason for Denial *
              </label>
              <textarea
                id="denialReason"
                value={denialReason}
                onChange={(e) => setDenialReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="E.g., Kit needs maintenance, not approved for this event"
                rows={4}
                required
              />
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDenialModal(null);
                  setDenialReason('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDenyConfirm}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Confirm Denial
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApprovalDashboard;
