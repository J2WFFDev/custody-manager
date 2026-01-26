import React, { useRef } from 'react';
import { kitService } from '../services/kitService';

interface QRCodeDisplayProps {
  kitId: number;
  kitName: string;
  kitCode: string;
  onClose: () => void;
}

const QRCodeDisplay: React.FC<QRCodeDisplayProps> = ({ kitId, kitName, kitCode, onClose }) => {
  const printRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert('Please allow popups to print the QR code');
      return;
    }

    const qrUrl = kitService.getQrCodeUrl(kitId, 'png');
    
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>QR Code - ${kitName}</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              margin: 0;
              padding: 20px;
            }
            .qr-container {
              text-align: center;
              border: 2px solid #000;
              padding: 30px;
              max-width: 400px;
            }
            h1 {
              font-size: 24px;
              margin: 0 0 10px 0;
            }
            .kit-code {
              font-size: 18px;
              font-weight: bold;
              margin: 0 0 20px 0;
              color: #333;
            }
            img {
              max-width: 100%;
              height: auto;
            }
            .instructions {
              margin-top: 20px;
              font-size: 12px;
              color: #666;
            }
            @media print {
              body {
                padding: 0;
              }
            }
          </style>
        </head>
        <body>
          <div class="qr-container">
            <h1>${kitName}</h1>
            <div class="kit-code">Code: ${kitCode}</div>
            <img src="${qrUrl}" alt="QR Code for ${kitName}" />
            <div class="instructions">
              Scan this QR code to check out/in this kit
            </div>
          </div>
          <script>
            window.onload = function() {
              window.print();
            };
          </script>
        </body>
      </html>
    `);
    
    printWindow.document.close();
  };

  const qrUrl = kitService.getQrCodeUrl(kitId, 'png');

  return (
    <div className="space-y-4">
      {/* Success Message */}
      <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-green-700">
              <strong>Kit registered successfully!</strong> QR code has been generated.
            </p>
          </div>
        </div>
      </div>

      {/* QR Code Display */}
      <div ref={printRef} className="bg-white border-2 border-gray-300 rounded-lg p-6 text-center">
        <h3 className="text-xl font-bold text-gray-800 mb-2">{kitName}</h3>
        <p className="text-gray-600 mb-4">Code: <strong>{kitCode}</strong></p>
        
        <div className="flex justify-center mb-4">
          <div className="bg-white p-4 border-2 border-gray-200 rounded-lg inline-block">
            <img
              src={qrUrl}
              alt={`QR Code for ${kitName}`}
              className="w-64 h-64"
            />
          </div>
        </div>
        
        <p className="text-sm text-gray-500">
          Scan this QR code to check out or check in this kit
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handlePrint}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Print QR Code
        </button>
        <button
          onClick={onClose}
          className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 transition-colors"
        >
          Done
        </button>
      </div>

      {/* Additional Info */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
        <p className="text-sm text-blue-700">
          <strong>Next Steps:</strong>
        </p>
        <ul className="list-disc list-inside text-sm text-blue-700 mt-2 space-y-1">
          <li>Print the QR code and attach it to the kit</li>
          <li>Store the kit in the designated location</li>
          <li>The kit is now ready for checkout/check-in operations</li>
        </ul>
      </div>
    </div>
  );
};

export default QRCodeDisplay;
