```python
"""
Automated Purchase Order Suggestion Generator

This module generates intelligent purchase order suggestions by integrating supplier data,
optimizing costs, and handling minimum order quantities. It analyzes current inventory levels,
demand forecasts, and supplier constraints to recommend optimal purchasing decisions.

Features:
- Multi-supplier cost comparison and optimization
- Minimum order quantity (MOQ) compliance
- Bulk discount tier analysis
- Lead time consideration
- Automated PO suggestion generation
- JSON-based data persistence

Usage: python script.py
"""

import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import math


@dataclass
class Supplier:
    """Represents a supplier with pricing and constraint information."""
    id: str
    name: str
    base_price: float
    moq: int  # Minimum Order Quantity
    lead_time_days: int
    bulk_discounts: List[Tuple[int, float]]  # (quantity_threshold, discount_percent)
    reliability_score: float  # 0.0 to 1.0


@dataclass
class InventoryItem:
    """Represents an inventory item with current stock and demand data."""
    sku: str
    name: str
    current_stock: int
    reorder_point: int
    weekly_demand: float
    safety_stock: int


@dataclass
class PurchaseOrderSuggestion:
    """Represents a suggested purchase order."""
    sku: str
    supplier_id: str
    supplier_name: str
    quantity: int
    unit_price: float
    total_cost: float
    delivery_date: str
    reasoning: str


class PurchaseOrderGenerator:
    """Main class for generating automated purchase order suggestions."""
    
    def __init__(self):
        self.suppliers = self._load_sample_suppliers()
        self.inventory = self._load_sample_inventory()
        
    def _load_sample_suppliers(self) -> Dict[str, List[Supplier]]:
        """Load sample supplier data organized by SKU."""
        suppliers_data = {
            "WIDGET001": [
                Supplier("SUP001", "Alpha Electronics", 12.50, 100, 5, [(500, 5.0), (1000, 10.0)], 0.95),
                Supplier("SUP002", "Beta Components", 11.75, 200, 7, [(1000, 8.0)], 0.88),
                Supplier("SUP003", "Gamma Supply", 13.20, 50, 3, [(300, 3.0), (800, 7.0)], 0.92)
            ],
            "WIDGET002": [
                Supplier("SUP001", "Alpha Electronics", 8.30, 150, 5, [(600, 6.0)], 0.95),
                Supplier("SUP004", "Delta Industries", 7.95, 250, 10, [(500, 4.0), (1500, 12.0)], 0.85)
            ],
            "COMPONENT_A": [
                Supplier("SUP002", "Beta Components", 5.40, 500, 7, [(2000, 10.0)], 0.88),
                Supplier("SUP005", "Epsilon Materials", 5.15, 300, 4, [(1000, 5.0), (2500, 15.0)], 0.90)
            ]
        }
        return suppliers_data
    
    def _load_sample_inventory(self) -> List[InventoryItem]:
        """Load sample inventory data."""
        return [
            InventoryItem("WIDGET001", "Premium Widget", 45, 100, 25.0, 50),
            InventoryItem("WIDGET002", "Standard Widget", 180, 200, 40.0, 75),
            InventoryItem("COMPONENT_A", "Component Alpha", 320, 500, 80.0, 150)
        ]
    
    def calculate_effective_price(self, supplier: Supplier, quantity: int) -> float:
        """Calculate the effective unit price including bulk discounts."""
        try:
            effective_price = supplier.base_price
            
            # Apply highest applicable discount
            applicable_discount = 0.0
            for threshold, discount in supplier.bulk_discounts:
                if quantity >= threshold:
                    applicable_discount = max(applicable_discount, discount)
            
            effective_price *= (1 - applicable_discount / 100)
            return round(effective_price, 2)
            
        except Exception as e:
            print(f"Error calculating effective price: {e}")
            return supplier.base_price
    
    def calculate_order_quantity(self, item: InventoryItem, supplier: Supplier) -> int:
        """Calculate optimal order quantity considering MOQ and demand."""
        try:
            # Calculate weeks of supply needed
            weeks_supply = 4 + (supplier.lead_time_days / 7)  # 4 weeks base + lead time
            demand_quantity = int(item.weekly_demand * weeks_supply)
            
            # Add safety stock if below reorder point
            if item.current_stock <= item.reorder_point:
                target_quantity = demand_quantity + item.safety_stock
            else:
                target_quantity = max(0, item.reorder_point - item.current_stock + demand_quantity)
            
            # Ensure MOQ compliance
            if target_quantity > 0:
                return max(target_quantity, supplier.moq)
            
            return 0
            
        except Exception as e:
            print(f"Error calculating order quantity: {e}")
            return supplier.moq
    
    def evaluate_supplier_score(self, supplier: Supplier, quantity: int, 
                              effective_price: float) -> float:
        """Calculate a composite supplier score for ranking."""
        try:
            # Normalize price component (lower is better, scale 0-1)
            price_score = 1 / (1 + effective_price / 10)
            
            # Lead time score (faster is better)
            lead_time_score = 1 / (1 + supplier.lead_time_days / 10)
            
            # Reliability score (already 0-1)
            reliability_score = supplier.reliability_score
            
            # MOQ efficiency (how much over MOQ we're ordering)
            moq_efficiency = min(quantity / supplier.moq, 2.0) / 2.0  # Cap at 2x MOQ
            
            # Weighted composite score
            composite_score = (
                price_score * 0.4 +
                reliability_score * 0.3 +
                lead_time_score * 0.2 +
                moq_efficiency * 0.1
            )
            
            return round(composite_score, 3)
            
        except Exception as e:
            print(f"Error calculating supplier score: {e}")
            return 0.0
    
    def generate_po_suggestions(self) -> List[PurchaseOrderSuggestion]:
        """Generate purchase order suggestions for all inventory items."""
        suggestions = []
        
        try:
            for item in self.inventory:
                if item.sku not in self.suppliers:
                    print(f"Warning: No suppliers found for {item.sku}")
                    continue
                
                # Skip if stock is adequate
                if item.current_stock > item.reorder_point:
                    continue
                
                best_supplier = None
                best_score = 0.0
                best_quantity = 0
                best_price = 0.0
                
                # Evaluate each supplier
                for supplier in self.suppliers[item.sku]:
                    quantity = self.calculate_order_quantity(item, supplier)
                    
                    if quantity > 0:
                        effective_price = self.calculate_effective_price(supplier, quantity)
                        score = self.evaluate_supplier_score(supplier, quantity, effective_price)
                        
                        if score > best_score:
                            best_score = score
                            best_supplier = supplier
                            best_quantity = quantity
                            best_price = effective_price
                
                # Create suggestion for best supplier
                if best_supplier:
                    delivery_date = (
                        datetime.datetime.now() +