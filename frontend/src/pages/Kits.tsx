import React, { useState, useEffect } from 'react';
import type { Kit } from '../types/kit';
import { KitStatus } from '../types/kit';
import { kitService } from '../services/kitService';
import Modal from '../components/Modal';
import KitRegistrationForm from '../components/KitRegistrationForm';
import QRCodeDisplay from '../components/QRCodeDisplay';
import CheckoutModal from '../components/CheckoutModal';
import OffSiteCheckoutModal from '../components/OffSiteCheckoutModal';
import TransferCustodyModal from '../components/TransferCustodyModal';
import type { CustodyCheckoutResponse, OffSiteCheckoutResponse, CustodyTransferResponse } from '../types/custody';
import MaintenanceModal from '../components/MaintenanceModal';
import LostFoundModal from '../components/LostFoundModal';
import type { CustodyCheckoutResponse, OffSiteCheckoutResponse, LostFoundResponse } from '../types/custody';
import WarningBadge from '../components/WarningBadge';
import type { CustodyCheckoutResponse, OffSiteCheckoutResponse } from '../types/custody';
import type { MaintenanceOpenResponse, MaintenanceCloseResponse } from '../types/maintenance';

const Kits: React.FC = () => {
  const [kits, setKits] = useState<Kit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRegistrationModal, setShowRegistrationModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showOffSiteCheckoutModal, setShowOffSiteCheckoutModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);
  const [maintenanceMode, setMaintenanceMode] = useState<'open' | 'close'>('open');
  const [showLostFoundModal, setShowLostFoundModal] = useState(false);
  const [lostFoundMode, setLostFoundMode] = useState<'lost' | 'found'>('lost');
  const [selectedKit, setSelectedKit] = useState<Kit | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load kits on component mount
  useEffect(() => {
    loadKits();
  }, []);

  const loadKits = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedKits = await kitService.getAllKits();
      setKits(fetchedKits);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load kits');
    } finally {
      setLoading(false);
    }
  };

  const handleRegistrationSuccess = async (kitId: number) => {
    // Close registration modal
    setShowRegistrationModal(false);
    
    // Reload kits to get the new one
    await loadKits();
    
    // Find the newly created kit and show its QR code
    const newKit = await kitService.getKit(kitId);
    setSelectedKit(newKit);
    setShowQRModal(true);
  };

  const handleViewQR = (kit: Kit) => {
    setSelectedKit(kit);
    setShowQRModal(true);
  };

  const handleCheckout = (kit: Kit) => {
    setSelectedKit(kit);
    setShowCheckoutModal(true);
  };

  const handleCheckoutSuccess = async (response: CustodyCheckoutResponse) => {
    setShowCheckoutModal(false);
    setSelectedKit(null);
    setSuccessMessage(response.message);
    
    // Reload kits to update status
    await loadKits();
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  const handleOffSiteCheckout = (kit: Kit) => {
    setSelectedKit(kit);
    setShowOffSiteCheckoutModal(true);
  };

  const handleOffSiteCheckoutSuccess = async (response: OffSiteCheckoutResponse) => {
    setShowOffSiteCheckoutModal(false);
    setSelectedKit(null);
    setSuccessMessage(response.message);
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  const handleTransfer = (kit: Kit) => {
    setSelectedKit(kit);
    setShowTransferModal(true);
  };

  const handleTransferSuccess = async (response: CustodyTransferResponse) => {
    setShowTransferModal(false);
    setSelectedKit(null);
    setSuccessMessage(response.message);
    
    // Reload kits to update custodian
    await loadKits();
  };

  const handleOpenMaintenance = (kit: Kit) => {
    setSelectedKit(kit);
    setMaintenanceMode('open');
    setShowMaintenanceModal(true);
  };

  const handleCloseMaintenance = (kit: Kit) => {
    setSelectedKit(kit);
    setMaintenanceMode('close');
    setShowMaintenanceModal(true);
  };

  const handleMaintenanceSuccess = async (response: MaintenanceOpenResponse | MaintenanceCloseResponse) => {
    setShowMaintenanceModal(false);
    setSelectedKit(null);
    setSuccessMessage(response.message);
    
    // Reload kits to update maintenance status
    await loadKits();
  };

  const handleReportLost = (kit: Kit) => {
    setSelectedKit(kit);
    setLostFoundMode('lost');
    setShowLostFoundModal(true);
  };

  const handleReportFound = (kit: Kit) => {
    setSelectedKit(kit);
    setLostFoundMode('found');
    setShowLostFoundModal(true);
  };

  const handleLostFoundSuccess = async (response: LostFoundResponse) => {
    setShowLostFoundModal(false);
    setSelectedKit(null);
    setSuccessMessage(response.message);
    
    // Reload kits to update status
    await loadKits();
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  const getStatusBadgeColor = (status: KitStatus) => {
    switch (status) {
      case KitStatus.AVAILABLE:
        return 'bg-green-100 text-green-800';
      case KitStatus.CHECKED_OUT:
        return 'bg-blue-100 text-blue-800';
      case KitStatus.IN_MAINTENANCE:
        return 'bg-yellow-100 text-yellow-800';
      case KitStatus.LOST:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatStatus = (status: KitStatus) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-4xl font-bold text-gray-800">
          Kit Management
        </h1>
        <button
          onClick={() => setShowRegistrationModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-md"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Register New Kit
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
          <p className="text-green-700">{successMessage}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="text-gray-600">Loading kits...</div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && kits.length === 0 && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Kits Registered</h3>
          <p className="text-gray-600 mb-6">Get started by registering your first kit.</p>
          <button
            onClick={() => setShowRegistrationModal(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Register First Kit
          </button>
        </div>
      )}

      {/* Kits Grid */}
      {!loading && !error && kits.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {kits.map((kit) => (
            <div key={kit.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-xl font-semibold text-gray-800">
                  {kit.name}
                </h3>
                <div className="flex flex-col gap-2 items-end">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusBadgeColor(kit.status)}`}>
                    {formatStatus(kit.status)}
                  </span>
                  {/* Show warning badge if kit has warnings */}
                  <WarningBadge kit={kit} />
                </div>
              </div>
              
              <p className="text-gray-600 text-sm mb-2">
                Code: <strong>{kit.code}</strong>
              </p>
              
              {kit.description && (
                <p className="text-gray-500 text-sm mb-4 line-clamp-2">
                  {kit.description}
                </p>
              )}
              
              {kit.current_custodian_name && (
                <p className="text-gray-600 text-sm mb-4">
                  Custodian: <strong>{kit.current_custodian_name}</strong>
                </p>
              )}
              
              {/* Show expected return date if available */}
              {kit.expected_return_date && (
                <p className="text-gray-600 text-sm mb-4">
                  Expected Return: <strong>{new Date(kit.expected_return_date).toLocaleDateString()}</strong>
                </p>
              )}

              <div className="pt-4 border-t border-gray-200 space-y-2">
                {/* Checkout buttons - only show if kit is available */}
                {kit.status === KitStatus.AVAILABLE && (
                  <>
                    <button
                      onClick={() => handleCheckout(kit)}
                      className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-medium"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                      </svg>
                      Check Out (On-Premises)
                    </button>
                    <button
                      onClick={() => handleOffSiteCheckout(kit)}
                      className="w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors flex items-center justify-center gap-2 font-medium"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Request Off-Site Checkout
                    </button>
                    <button
                      onClick={() => handleOpenMaintenance(kit)}
                      className="w-full bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 transition-colors flex items-center justify-center gap-2 font-medium"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Open Maintenance
                    </button>
                  </>
                )}

                {/* Report Lost button - show for available or checked out kits */}
                {(kit.status === KitStatus.AVAILABLE || kit.status === KitStatus.CHECKED_OUT) && (
                  <button
                    onClick={() => handleReportLost(kit)}
                    className="w-full bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors flex items-center justify-center gap-2 font-medium"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Report Lost
                  </button>
                )}

                {/* Report Found button - only show for lost kits */}
                {kit.status === KitStatus.LOST && (
                  <button
                    onClick={() => handleReportFound(kit)}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-medium"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Report Found
                  </button>
                )}
                
                {/* Close maintenance button - only show if kit is in maintenance */}
                {kit.status === KitStatus.IN_MAINTENANCE && (
                  <button
                    onClick={() => handleCloseMaintenance(kit)}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-medium"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Close Maintenance
                  </button>
                )}
                
                {/* Transfer button - only show if kit is checked out */}
                {kit.status === KitStatus.CHECKED_OUT && (
                  <button
                    onClick={() => handleTransfer(kit)}
                    className="w-full bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition-colors flex items-center justify-center gap-2 font-medium"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                    Transfer Custody
                  </button>
                )}
                
                {/* View QR button */}
                <button
                  onClick={() => handleViewQR(kit)}
                  className="w-full bg-blue-50 text-blue-600 px-4 py-2 rounded hover:bg-blue-100 transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                  </svg>
                  View QR Code
                </button>
              </div>

              <div className="mt-2 text-xs text-gray-400">
                Created: {new Date(kit.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Registration Modal */}
      <Modal
        isOpen={showRegistrationModal}
        onClose={() => setShowRegistrationModal(false)}
        title="Register New Kit"
      >
        <KitRegistrationForm
          onSuccess={handleRegistrationSuccess}
          onCancel={() => setShowRegistrationModal(false)}
        />
      </Modal>

      {/* QR Code Display Modal */}
      <Modal
        isOpen={showQRModal}
        onClose={() => {
          setShowQRModal(false);
          setSelectedKit(null);
        }}
        title="QR Code"
      >
        {selectedKit && (
          <QRCodeDisplay
            kitId={selectedKit.id}
            kitName={selectedKit.name}
            kitCode={selectedKit.code}
            onClose={() => {
              setShowQRModal(false);
              setSelectedKit(null);
            }}
          />
        )}
      </Modal>

      {/* Checkout Modal */}
      {showCheckoutModal && selectedKit && (
        <CheckoutModal
          kitCode={selectedKit.code}
          onClose={() => {
            setShowCheckoutModal(false);
            setSelectedKit(null);
          }}
          onSuccess={handleCheckoutSuccess}
        />
      )}

      {/* Off-Site Checkout Modal */}
      {showOffSiteCheckoutModal && selectedKit && (
        <OffSiteCheckoutModal
          kitCode={selectedKit.code}
          onClose={() => {
            setShowOffSiteCheckoutModal(false);
            setSelectedKit(null);
          }}
          onSuccess={handleOffSiteCheckoutSuccess}
        />
      )}

      {/* Transfer Custody Modal */}
      {showTransferModal && selectedKit && (
        <TransferCustodyModal
          kitCode={selectedKit.code}
          currentCustodian={selectedKit.current_custodian_name || undefined}
          onClose={() => {
            setShowTransferModal(false);
            setSelectedKit(null);
          }}
          onSuccess={handleTransferSuccess}
        />
      )}

      {/* Maintenance Modal */}
      {showMaintenanceModal && selectedKit && (
        <MaintenanceModal
          kitCode={selectedKit.code}
          kitName={selectedKit.name}
          isOpen={showMaintenanceModal}
          mode={maintenanceMode}
          onClose={() => {
            setShowMaintenanceModal(false);
            setSelectedKit(null);
          }}
          onSuccess={handleMaintenanceSuccess}
        />
      )}

      {/* Lost/Found Modal */}
      {showLostFoundModal && selectedKit && (
        <LostFoundModal
          kitCode={selectedKit.code}
          mode={lostFoundMode}
          onClose={() => {
            setShowLostFoundModal(false);
            setSelectedKit(null);
          }}
          onSuccess={handleLostFoundSuccess}
        />
      )}
    </div>
  );
};

export default Kits;
