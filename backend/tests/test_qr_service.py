import pytest
from app.services.qr_service import generate_qr_code, create_qr_image

def test_generate_qr_code():
    """Test QR code generation"""
    qr_code = generate_qr_code()
    
    # Should be in format XXX-XXXX-XXXX
    assert isinstance(qr_code, str)
    assert len(qr_code) == 13  # 3 + 1 + 4 + 1 + 4
    assert qr_code.count("-") == 2
    
    # Split and verify parts
    parts = qr_code.split("-")
    assert len(parts) == 3
    assert len(parts[0]) == 3
    assert len(parts[1]) == 4
    assert len(parts[2]) == 4
    
    # All uppercase alphanumeric
    assert qr_code.replace("-", "").isalnum()
    assert qr_code.replace("-", "").isupper()

def test_qr_codes_are_unique():
    """Test that generated QR codes are unique"""
    codes = set()
    for _ in range(100):
        code = generate_qr_code()
        codes.add(code)
    
    # All codes should be unique
    assert len(codes) == 100

def test_create_qr_image_png():
    """Test creating QR code as PNG"""
    data = "TEST-QR-CODE"
    image_bytes = create_qr_image(data, "PNG")
    
    # Should return bytes
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    
    # PNG files start with specific bytes
    assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n'

def test_create_qr_image_svg():
    """Test creating QR code as SVG"""
    data = "TEST-QR-CODE"
    image_bytes = create_qr_image(data, "SVG")
    
    # Should return bytes
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    
    # SVG should contain XML/SVG tags
    svg_string = image_bytes.decode('utf-8')
    assert 'svg' in svg_string.lower()
