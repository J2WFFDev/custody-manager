import qrcode
import qrcode.image.svg
import io
import secrets
from typing import Literal

def generate_qr_code(qr_code: str) -> str:
    """
    Generate unique alphanumeric code for kits.
    
    Returns:
        Unique alphanumeric code (not exposing serial numbers per QR-004)
    """
    # Generate a 12-character alphanumeric code
    # Format: XXX-XXXX-XXXX for readability
    part1 = secrets.token_hex(2).upper()[:3]
    part2 = secrets.token_hex(2).upper()[:4]
    part3 = secrets.token_hex(2).upper()[:4]
    return f"{part1}-{part2}-{part3}"

def create_qr_image(data: str, image_format: Literal["PNG", "SVG"] = "PNG") -> bytes:
    """
    Create QR code image from data.
    
    Args:
        data: The data to encode in the QR code
        image_format: Output format (PNG or SVG)
        
    Returns:
        QR code image as bytes
    """
    if image_format == "SVG":
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=factory
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image()
        buffer = io.BytesIO()
        img.save(buffer)
        return buffer.getvalue()
    else:  # PNG
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
