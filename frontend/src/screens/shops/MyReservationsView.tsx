import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Booking } from '../../types/shops';
import { getBookingStatus } from '../../utils/shopHelpers';
import BookingCard from '../../components/shops/BookingCard';

interface MyReservationsViewProps {
  bookings: Booking[];
  onBack: () => void;
  onCancelBooking: (bookingId: string) => void;
  onRebookItem: (shopId: string, itemId: string) => void;
  onViewBookingDetail: (bookingId: string) => void;
}

export default function MyReservationsView({ bookings, onBack, onCancelBooking, onRebookItem, onViewBookingDetail }: MyReservationsViewProps) {
  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');

  const activeBookings = bookings.filter(b => {
    const status = getBookingStatus(b);
    return status === 'Active' || status === 'Expiring Soon';
  });

  const historyBookings = bookings.filter(b => {
    const status = getBookingStatus(b);
    return status === 'Expired' || status === 'Cancelled' || status === 'Picked Up';
  });

  const displayedBookings = activeTab === 'active' ? activeBookings : historyBookings;

  const handleCancelBooking = (booking: Booking) => {
    Alert.alert(
      'Cancel Reservation?',
      `Are you sure you want to cancel your reservation for "${booking.item.name}"?\n\nThe item will be returned to available stock.`,
      [
        { text: 'Keep Reservation', style: 'cancel' },
        { text: 'Cancel Reservation', style: 'destructive', onPress: () => onCancelBooking(booking.id) },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <FontAwesome name="arrow-left" size={20} color="#0C2340" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>My Reservations</Text>
        <View style={styles.placeholder} />
      </View>

      <View style={styles.tabContainer}>
        <TouchableOpacity style={[styles.tab, activeTab === 'active' && styles.tabActive]} onPress={() => setActiveTab('active')}>
          <Text style={[styles.tabText, activeTab === 'active' && styles.tabTextActive]}>Active ({activeBookings.length})</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tab, activeTab === 'history' && styles.tabActive]} onPress={() => setActiveTab('history')}>
          <Text style={[styles.tabText, activeTab === 'history' && styles.tabTextActive]}>History ({historyBookings.length})</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.list} showsVerticalScrollIndicator={false}>
        {displayedBookings.length === 0 ? (
          <View style={styles.emptyState}>
            <FontAwesome name={activeTab === 'active' ? 'ticket' : 'history'} size={48} color="#ccc" />
            <Text style={styles.emptyTitle}>{activeTab === 'active' ? 'No Active Reservations' : 'No Reservation History'}</Text>
            <Text style={styles.emptyText}>
              {activeTab === 'active'
                ? 'Items you reserve will appear here. Browse shops to find items to reserve for pickup.'
                : 'Your completed, cancelled, and expired reservations will appear here.'}
            </Text>
          </View>
        ) : (
          displayedBookings.map(booking => (
            <BookingCard
              key={booking.id}
              booking={booking}
              onPress={() => onViewBookingDetail(booking.id)}
              onCancel={activeTab === 'active' ? () => handleCancelBooking(booking) : undefined}
              onRebook={activeTab === 'history' ? () => onRebookItem(booking.shopId, booking.itemId) : undefined}
            />
          ))
        )}
        <View style={styles.bottomPadding} />
      </ScrollView>

      {activeTab === 'active' && activeBookings.length > 0 && (
        <View style={styles.infoFooter}>
          <FontAwesome name="info-circle" size={14} color="#666" />
          <Text style={styles.infoText}>Reservations are held for 24 hours. Present your pickup code at the shop to collect and pay for your items.</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  backButton: { padding: 8 },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#0C2340' },
  placeholder: { width: 36 },
  tabContainer: { flexDirection: 'row', backgroundColor: '#fff', paddingHorizontal: 16, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  tab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderBottomWidth: 2, borderBottomColor: 'transparent' },
  tabActive: { borderBottomColor: '#0C2340' },
  tabText: { fontSize: 14, fontWeight: '600', color: '#666' },
  tabTextActive: { color: '#0C2340' },
  list: { flex: 1, paddingHorizontal: 16, paddingTop: 12 },
  emptyState: { alignItems: 'center', paddingTop: 60, paddingHorizontal: 32 },
  emptyTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginTop: 16 },
  emptyText: { fontSize: 14, color: '#666', marginTop: 8, textAlign: 'center', lineHeight: 20 },
  bottomPadding: { height: 20 },
  infoFooter: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', paddingHorizontal: 16, paddingVertical: 12, borderTopWidth: 1, borderTopColor: '#e0e0e0', gap: 8 },
  infoText: { flex: 1, fontSize: 12, color: '#666', lineHeight: 16 },
});