import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Booking } from '../../types/shops';
import { formatPrice, formatDate, getBookingStatus } from '../../utils/shopHelpers';
import StatusBadge from './StatusBadge';
import CountdownTimer from './CountdownTimer';

interface BookingCardProps {
  booking: Booking;
  onPress: () => void;
  onCancel?: () => void;
  onRebook?: () => void;
}

export default function BookingCard({ booking, onPress, onCancel, onRebook }: BookingCardProps) {
  const status = getBookingStatus(booking);
  const isActive = status === 'Active' || status === 'Expiring Soon';
  const canRebook = status === 'Cancelled' || status === 'Expired';
    // Safely access shop and item properties
  const shopName = booking.shop?.name || 'Unknown Shop';
  const itemName = booking.item?.name || 'Unknown Item';
  const shopLocation = booking.shop?.location || 'Unknown Location';
  const shopGate = booking.shop?.gate;

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.header}>
        <View style={styles.shopInfo}>
          <Text style={styles.shopName}>{shopName}</Text>
          <Text style={styles.itemName}>{itemName}</Text>
        </View>
        <StatusBadge status={status} />
      </View>

      <View style={styles.details}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Quantity:</Text>
          <Text style={styles.detailValue}>{booking.quantity}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Estimated Total:</Text>
          <Text style={styles.detailValue}>{formatPrice(booking.totalPrice)}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Payment:</Text>
          <Text style={styles.payAtShopValue}>Pay at shop</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Pickup Code:</Text>
          <Text style={styles.pickupCode}>{booking.pickupCode}</Text>
        </View>
      </View>

      {isActive && (
        <View style={styles.countdownContainer}>
          <Text style={styles.countdownLabel}>Time remaining to pickup:</Text>
          <CountdownTimer expiresAt={booking.expiresAt} size="small" />
        </View>
      )}

      <View style={styles.locationInfo}>
        <FontAwesome name="map-marker" size={12} color="#666" />
        <Text style={styles.locationText}>
          Pickup at {shopLocation}
          {shopGate ? ` · ${shopGate}` : ''}
        </Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.bookingDate}>Reserved {formatDate(booking.createdAt)}</Text>
        {isActive && onCancel && (
          <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
            <FontAwesome name="times" size={12} color="#C62828" />
            <Text style={styles.cancelText}>Cancel</Text>
          </TouchableOpacity>
        )}
        {canRebook && onRebook && (
          <TouchableOpacity style={styles.rebookButton} onPress={onRebook}>
            <FontAwesome name="refresh" size={12} color="#1976D2" />
            <Text style={styles.rebookText}>Reserve Again</Text>
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 4, elevation: 2 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  shopInfo: { flex: 1, marginRight: 12 },
  shopName: { fontSize: 12, color: '#666', marginBottom: 2 },
  itemName: { fontSize: 16, fontWeight: 'bold', color: '#0C2340' },
  details: { backgroundColor: '#f8f8f8', borderRadius: 8, padding: 12, marginBottom: 12 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  detailLabel: { fontSize: 13, color: '#666' },
  detailValue: { fontSize: 13, fontWeight: '600', color: '#333' },
  payAtShopValue: { fontSize: 13, fontWeight: '600', color: '#4CAF50' },
  pickupCode: { fontSize: 14, fontWeight: 'bold', color: '#0C2340', letterSpacing: 2, fontVariant: ['tabular-nums'] },
  countdownContainer: { backgroundColor: '#FFF8E1', borderRadius: 8, padding: 12, marginBottom: 12, alignItems: 'center' },
  countdownLabel: { fontSize: 12, color: '#666', marginBottom: 8 },
  locationInfo: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 12 },
  locationText: { fontSize: 12, color: '#666' },
  footer: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderTopWidth: 1, borderTopColor: '#f0f0f0', paddingTop: 12 },
  bookingDate: { fontSize: 11, color: '#999' },
  cancelButton: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#FFEBEE', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16 },
  cancelText: { fontSize: 12, color: '#C62828', fontWeight: '600' },
  rebookButton: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#E3F2FD', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16 },
  rebookText: { fontSize: 12, color: '#1976D2', fontWeight: '600' },
});