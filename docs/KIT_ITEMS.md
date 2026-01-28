# Kit Items Feature

## Overview

The Kit Items feature enables granular tracking of individual components within a kit. Instead of treating a kit as a single monolithic entity, each kit can now contain multiple trackable items such as firearms, optics, cases, magazines, tools, and accessories.

## Architecture

### Data Model

**Kit** (Container)
- Existing kit model with all previous attributes
- New `items` relationship to KitItem

**KitItem** (Component)
- `id` - Unique identifier
- `kit_id` - Foreign key to parent kit
- `item_type` - Type of item (firearm, optic, case, magazine, tool, accessory, etc.)
- `make` - Manufacturer/brand
- `model` - Model name/number
- `serial_number` - Encrypted serial number (nullable)
- `friendly_name` - User-friendly identifier (e.g., "Primary Rifle")
- `photo_url` - URL to item photo
- `quantity` - Quantity for bulk items (e.g., magazines)
- `status` - Current status (in_kit, checked_out, lost, maintenance)
- `notes` - Additional notes

### API Endpoints

All kit item endpoints are nested under the kit resource:

```
GET    /api/v1/kits/{kit_id}/items              List items in a kit
POST   /api/v1/kits/{kit_id}/items              Add item to a kit
GET    /api/v1/kits/{kit_id}/items/{item_id}    Get item details
PUT    /api/v1/kits/{kit_id}/items/{item_id}    Update an item
DELETE /api/v1/kits/{kit_id}/items/{item_id}    Remove item from kit
```

### Frontend Components

**KitItemsList** - Displays all items in a kit with add/edit/delete actions
**KitItemForm** - Form for creating or updating kit items
**KitDetails** - Page showing kit information and its items

## Usage Examples

### Backend (Python)

```python
# Create a kit item
from app.models import KitItem

item = KitItem(
    kit_id=1,
    item_type="firearm",
    make="Ruger",
    model="10/22",
    serial_number="SN-12345",
    friendly_name="Primary Rifle",
    quantity=1
)
```

### Frontend (TypeScript)

```typescript
// Get all items in a kit
const items = await kitItemService.getKitItems(kitId);

// Add a new item
await kitItemService.createKitItem(kitId, {
    item_type: "optic",
    make: "Vortex",
    model: "Crossfire II",
    serial_number: "OPT-789"
});
```

## Security

- Serial numbers are encrypted at rest using the same encryption as kit serial numbers
- All kit item operations require appropriate authentication
- Cascade delete ensures orphaned items are automatically removed

## Migration Strategy

For existing kits:
1. Kits continue to function as before with backward compatibility
2. Administrators can optionally add component items to existing kits
3. The original kit-level serial number remains separate from item-level serials

## Benefits

✅ Granular tracking of individual components
✅ Support for swapping/replacing broken items
✅ Better compliance and audit trails
✅ Flexible inventory management
✅ Individual serial number tracking per component
✅ Component-level status tracking
