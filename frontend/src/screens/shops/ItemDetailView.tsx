import React, { useState, useMemo } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Shop, Item, Booking, SelectedVariant, Variant } from '../../types/shops';
import { formatPrice, getBookingStatus } from '../../utils/shopHelpers';
import { CreateBookingParams } from '../../services/shopService';
import StatusBadge from '../../components/shops/StatusBadge';

interface ItemDetailViewProps {
  shop: Shop;
  item: Item;
  existingBookings: Booking[];
  onBack: () => void;
  onBook: (params: CreateBookingParams) => Promise<Booking>;
}

const MAX_BOOKING_QUANTITY = 3;

export default function ItemDetailView({ shop, item, existingBookings, onBack, onBook }: ItemDetailViewProps) {
  const [quantity, setQuantity] = useState(1);
  const [selectedVariants, setSelectedVariants] = useState<SelectedVariant[]>([]);
  const [isBooking, setIsBooking] = useState(false);

  const variantsByType = useMemo(() => {
    const grouped: Record<string, Variant[]> = {};
    item.variants.forEach(variant => {
      if (!grouped[variant.variantType]) grouped[variant.variantType] = [];
      grouped[variant.variantType].push(variant);
    });
    return grouped;
  }, [item.variants]);

  const existingBookingForItem = existingBookings.find(
    b => b.itemId === item.id && (getBookingStatus(b) === 'Active' || getBookingStatus(b) === 'Expiring Soon')
  );

  const calculateTotalPrice = () => {
    let total = item.basePrice * quantity;
    selectedVariants.forEach(v => {
      total += v.priceAdjustment * quantity;
    });
    return total;
  };

  const selectVariant = (variantType: string, variant: Variant) => {
    setSelectedVariants(prev => {
      const filtered = prev.filter(v => v.variantType !== variantType);
      return [...filtered, { variantType: variant.variantType, variantValue: variant.variantValue, priceAdjustment: variant.priceAdjustment }];
    });
  };

  const isVariantSelected = (variantType: string, variantValue: string) => {
    return selectedVariants.some(v => v.variantType === variantType && v.variantValue === variantValue);
  };

  const canBook = () => {
    if (existingBookingForItem) return false;
    if (item.availability === 'Out of Stock') return false;
    if (quantity > MAX_BOOKING_QUANTITY) return false;
    return true;
  };

  const handleBook = async () => {
    if (!canBook()) {
      if (existingBookingForItem) {
        Alert.alert('Already Reserved', 'You already have an active reservation for this item.');
      } else if (item.availability === 'Out of Stock') {
        Alert.alert('Out of Stock', 'This item is currently out of stock.');
      }
      return;
    }

    setIsBooking(true);
    try {
      const booking = await onBook({
        itemId: item.id,
        shopId: shop.id,
        quantity: quantity,
        selectedVariants: selectedVariants.length > 0 ? selectedVariants : undefined,
      });
      Alert.alert(
        'Reservation Confirmed! ✓',
        `Your item has been reserved for 24 hours.\n\nPickup Code: ${booking.pickupCode}\nLocation: ${shop.location}\n\nNo payment taken - pay at the shop when you collect your item.`,
        [{ text: 'OK', onPress: onBack }]
      );
    } catch (error) {
      Alert.alert('Reservation Failed', error instanceof Error ? error.message : 'An error occurred. Please try again.', [{ text: 'OK' }]);
    } finally {
      setIsBooking(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <FontAwesome name="arrow-left" size={20} color="#0C2340" />
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{item.name}</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.imageContainer}>
          <FontAwesome name="shopping-basket" size={64} color="#0C2340" />
        </View>

        <View style={styles.infoCard}>
          <View style={styles.infoHeader}>
            <Text style={styles.itemName}>{item.name}</Text>
            <StatusBadge status={item.availability} />
          </View>
          <Text style={styles.itemPrice}>{formatPrice(item.basePrice, item.currency)}</Text>
          <Text style={styles.itemDescription}>{item.description}</Text>
        </View>

        {item.variantTypes.length > 0 && (
          <View style={styles.optionsCard}>
            <Text style={styles.sectionTitle}>Options</Text>
            {Object.entries(variantsByType).map(([type, variants]) => (
              <View key={type} style={styles.optionGroup}>
                <Text style={styles.optionLabel}>{type}</Text>
                <View style={styles.optionButtons}>
                  {variants.map(variant => (
                    <TouchableOpacity
                      key={`${variant.variantType}-${variant.variantValue}`}
                      style={[styles.optionButton, isVariantSelected(variant.variantType, variant.variantValue) && styles.optionButtonSelected]}
                      onPress={() => selectVariant(type, variant)}
                    >
                      <Text style={[styles.optionButtonText, isVariantSelected(variant.variantType, variant.variantValue) && styles.optionButtonTextSelected]}>
                        {variant.variantValue}
                      </Text>
                      {variant.priceAdjustment !== 0 && (
                        <Text style={[styles.optionPriceModifier, isVariantSelected(variant.variantType, variant.variantValue) && styles.optionPriceModifierSelected]}>
                          {variant.priceAdjustment > 0 ? '+' : ''}{formatPrice(variant.priceAdjustment, item.currency)}
                        </Text>
                      )}
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            ))}
          </View>
        )}

        <View style={styles.quantityCard}>
          <Text style={styles.sectionTitle}>Quantity</Text>
          <View style={styles.quantitySelector}>
            <TouchableOpacity style={styles.quantityButton} onPress={() => setQuantity(Math.max(1, quantity - 1))}>
              <FontAwesome name="minus" size={16} color="#0C2340" />
            </TouchableOpacity>
            <Text style={styles.quantityText}>{quantity}</Text>
            <TouchableOpacity style={styles.quantityButton} onPress={() => setQuantity(Math.min(MAX_BOOKING_QUANTITY, quantity + 1))}>
              <FontAwesome name="plus" size={16} color="#0C2340" />
            </TouchableOpacity>
          </View>
          <Text style={styles.quantityHint}>Maximum {MAX_BOOKING_QUANTITY} per reservation</Text>
        </View>

        <View style={styles.bookingInfoCard}>
          <FontAwesome name="info-circle" size={18} color="#1976D2" />
          <View style={styles.bookingInfoContent}>
            <Text style={styles.bookingInfoTitle}>24-Hour Reservation (No Payment Required)</Text>
            <Text style={styles.bookingInfoText}>
              This is a reservation only - no payment is taken now. Your item will be held for 24 hours. Visit {shop.location} during shop hours, show your pickup code, and pay at the counter when collecting your item.
            </Text>
          </View>
        </View>

        {existingBookingForItem && (
          <View style={styles.warningCard}>
            <FontAwesome name="exclamation-triangle" size={18} color="#E65100" />
            <Text style={styles.warningText}>You already have an active reservation for this item.</Text>
          </View>
        )}

        <View style={styles.bottomPadding} />
      </ScrollView>

      <View style={styles.footer}>
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Estimated Total</Text>
          <Text style={styles.totalPrice}>{formatPrice(calculateTotalPrice(), item.currency)}</Text>
          <Text style={styles.payAtShopText}>Pay at shop</Text>
        </View>
        <TouchableOpacity
          style={[styles.bookButton, (!canBook() || isBooking) && styles.bookButtonDisabled]}
          onPress={handleBook}
          disabled={!canBook() || isBooking}
        >
          {isBooking ? (
            <Text style={styles.bookButtonText}>Reserving...</Text>
          ) : (
            <>
              <FontAwesome name="clock-o" size={18} color="#fff" />
              <Text style={styles.bookButtonText}>Reserve for 24 Hours</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  backButton: { padding: 8 },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#0C2340', flex: 1, textAlign: 'center', marginHorizontal: 8 },
  placeholder: { width: 36 },
  content: { flex: 1 },
  imageContainer: { height: 200, backgroundColor: '#f5f5f5', justifyContent: 'center', alignItems: 'center' },
  infoCard: { backgroundColor: '#fff', padding: 16, marginBottom: 12 },
  infoHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 },
  itemName: { fontSize: 20, fontWeight: 'bold', color: '#0C2340', flex: 1, marginRight: 12 },
  itemPrice: { fontSize: 24, fontWeight: 'bold', color: '#0C2340', marginBottom: 12 },
  itemDescription: { fontSize: 14, color: '#666', lineHeight: 20 },
  optionsCard: { backgroundColor: '#fff', padding: 16, marginBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#0C2340', marginBottom: 12 },
  optionGroup: { marginBottom: 16 },
  optionLabel: { fontSize: 14, fontWeight: '600', color: '#333', marginBottom: 8 },
  optionButtons: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  optionButton: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 8, borderWidth: 1, borderColor: '#e0e0e0', backgroundColor: '#fff' },
  optionButtonSelected: { borderColor: '#0C2340', backgroundColor: '#0C2340' },
  optionButtonText: { fontSize: 14, color: '#333', fontWeight: '500' },
  optionButtonTextSelected: { color: '#FFD100' },
  optionPriceModifier: { fontSize: 12, color: '#666', marginTop: 2 },
  optionPriceModifierSelected: { color: '#FFD100' },
  quantityCard: { backgroundColor: '#fff', padding: 16, marginBottom: 12 },
  quantitySelector: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 24 },
  quantityButton: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#FFD100', justifyContent: 'center', alignItems: 'center' },
  quantityText: { fontSize: 24, fontWeight: 'bold', color: '#0C2340', minWidth: 40, textAlign: 'center' },
  quantityHint: { textAlign: 'center', fontSize: 12, color: '#666', marginTop: 8 },
  bookingInfoCard: { flexDirection: 'row', backgroundColor: '#E3F2FD', marginHorizontal: 16, padding: 16, borderRadius: 12, gap: 12, marginBottom: 12 },
  bookingInfoContent: { flex: 1 },
  bookingInfoTitle: { fontSize: 14, fontWeight: 'bold', color: '#1976D2', marginBottom: 4 },
  bookingInfoText: { fontSize: 13, color: '#1976D2', lineHeight: 18 },
  warningCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFF3E0', marginHorizontal: 16, padding: 16, borderRadius: 12, gap: 12, marginBottom: 12 },
  warningText: { flex: 1, fontSize: 14, color: '#E65100' },
  bottomPadding: { height: 20 },
  footer: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', paddingHorizontal: 16, paddingVertical: 12, borderTopWidth: 1, borderTopColor: '#e0e0e0', gap: 16 },
  totalContainer: { alignItems: 'flex-start' },
  totalLabel: { fontSize: 12, color: '#666' },
  totalPrice: { fontSize: 20, fontWeight: 'bold', color: '#0C2340' },
  payAtShopText: { fontSize: 10, color: '#4CAF50', fontWeight: '500' },
  bookButton: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0C2340', paddingVertical: 14, borderRadius: 12, gap: 8 },
  bookButtonDisabled: { backgroundColor: '#ccc' },
  bookButtonText: { fontSize: 16, fontWeight: 'bold', color: '#fff' },
});