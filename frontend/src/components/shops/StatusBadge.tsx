import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AvailabilityStatus, BookingStatus } from '../../types/shops';

interface StatusBadgeProps {
  status: AvailabilityStatus | BookingStatus | 'Open' | 'Closed';
  size?: 'small' | 'medium';
}

export default function StatusBadge({ status, size = 'medium' }: StatusBadgeProps) {
  const getStatusStyle = () => {
    switch (status) {
      case 'In Stock':
      case 'Active':
      case 'Open':
        return { bg: '#E8F5E9', text: '#2E7D32' };
      case 'Low Stock':
      case 'Expiring Soon':
        return { bg: '#FFF3E0', text: '#E65100' };
      case 'Out of Stock':
      case 'Expired':
      case 'Closed':
        return { bg: '#FFEBEE', text: '#C62828' };
      case 'Picked Up':
        return { bg: '#E3F2FD', text: '#1565C0' };
      case 'Cancelled':
        return { bg: '#F5F5F5', text: '#616161' };
      default:
        return { bg: '#F5F5F5', text: '#666' };
    }
  };

  const colors = getStatusStyle();
  const fontSize = size === 'small' ? 10 : 12;
  const padding = size === 'small' ? { paddingHorizontal: 6, paddingVertical: 2 } : { paddingHorizontal: 10, paddingVertical: 4 };

  return (
    <View style={[styles.badge, { backgroundColor: colors.bg }, padding]}>
      <Text style={[styles.text, { color: colors.text, fontSize }]}>{status}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: { borderRadius: 12, alignSelf: 'flex-start' },
  text: { fontWeight: '600' },
});