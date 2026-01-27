import React from 'react';

interface AttestationDisplayProps {
  attestationText: string;
  signature: string;
  onSignatureChange: (signature: string) => void;
  accepted: boolean;
  onAcceptedChange: (accepted: boolean) => void;
  disabled?: boolean;
}

/**
 * AttestationDisplay component - Displays legal attestation text and captures user acknowledgment
 * Implements CUSTODY-012: Responsibility attestation for off-site custody
 */
const AttestationDisplay: React.FC<AttestationDisplayProps> = ({
  attestationText,
  signature,
  onSignatureChange,
  accepted,
  onAcceptedChange,
  disabled = false
}) => {
  return (
    <div className="space-y-4">
      {/* Legal Disclaimer Header */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4">
        <div className="flex items-start">
          <svg className="w-6 h-6 text-amber-500 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-amber-800 mb-1">Legal Responsibility Attestation Required</h3>
            <p className="text-sm text-amber-700">
              Please read the following terms carefully before requesting off-site custody.
            </p>
          </div>
        </div>
      </div>

      {/* Attestation Text Display */}
      <div 
        className="border border-gray-300 rounded-lg p-4 bg-gray-50 max-h-80 overflow-y-auto"
        role="region"
        aria-label="Legal attestation text"
        tabIndex={0}
      >
        <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans leading-relaxed">
          {attestationText}
        </pre>
      </div>

      {/* Digital Signature Input */}
      <div>
        <label htmlFor="attestation-signature" className="block text-sm font-medium text-gray-700 mb-2">
          Digital Signature *
        </label>
        <input
          type="text"
          id="attestation-signature"
          value={signature}
          onChange={(e) => onSignatureChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Type your full legal name"
          required
          disabled={disabled}
        />
        <p className="text-xs text-gray-500 mt-1">
          By typing your name, you are providing a digital signature confirming your agreement.
        </p>
      </div>

      {/* Acceptance Checkbox */}
      <div className="flex items-start">
        <input
          type="checkbox"
          id="attestation-accepted"
          checked={accepted}
          onChange={(e) => onAcceptedChange(e.target.checked)}
          className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          required
          disabled={disabled}
        />
        <label htmlFor="attestation-accepted" className="ml-3 text-sm text-gray-700">
          <span className="font-semibold">I have read and agree to all terms and conditions above.</span>
          <br />
          <span className="text-xs text-gray-600">
            I understand that I am accepting full legal responsibility for the firearm kit while in my custody.
          </span>
        </label>
      </div>

      {/* Warning if not accepted */}
      {!accepted && signature && (
        <div className="bg-red-50 border-l-4 border-red-500 p-3">
          <p className="text-sm text-red-700">
            You must check the box to confirm you have read and accept the terms before proceeding.
          </p>
        </div>
      )}
    </div>
  );
};

export default AttestationDisplay;
