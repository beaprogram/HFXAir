import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Shop } from '../../types/shops';
import { getShopStatusText, formatTime } from '../../utils/shopHelpers';
import StatusBadge from './StatusBadge';

interface ShopCardProps {
  shop: Shop;
  onPress: () => void;
}

export default function ShopCard({ shop, onPress }: ShopCardProps) {
  const status = getShopStatusText(shop);

  const getCategoryIcon = (category: string) => {
    const lowerCategory = category.toLowerCase();
    if (lowerCategory.includes('food') || lowerCategory.includes('beverage')) return 'cutlery';
    if (lowerCategory.includes('book') || lowerCategory.includes('magazine')) return 'book';
    if (lowerCategory.includes('souvenir') || lowerCategory.includes('gift') || lowerCategory.includes('duty')) return 'gift';
    if (lowerCategory.includes('electronics')) return 'laptop';
    if (lowerCategory.includes('health') || lowerCategory.includes('beauty')) return 'heart';
    return 'shopping-bag';
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.cardHeader}>
        <View style={styles.iconContainer}>
          <FontAwesome name={getCategoryIcon(shop.category)} size={24} color="#0C2340" />
        </View>
        <View style={styles.shopInfo}>
          <Text style={styles.shopName}>{shop.name}</Text>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{shop.category}</Text>
          </View>
        </View>
        <FontAwesome name="chevron-right" size={16} color="#ccc" />
      </View>

      <Text style={styles.description} numberOfLines={2}>{shop.description}</Text>

      <View style={styles.detailsContainer}>
        <View style={styles.detailItem}>
          <FontAwesome name="map-marker" size={14} color="#666" />
          <Text style={styles.detailText}>{shop.location}</Text>
        </View>
        {shop.todayHours && (
          <View style={styles.detailItem}>
            <FontAwesome name="clock-o" size={14} color="#666" />
            <Text style={styles.detailText}>
              {formatTime(shop.todayHours.openTime)} - {formatTime(shop.todayHours.closeTime)}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.statusContainer}>
        <StatusBadge status={status.isOpen ? 'Open' : 'Closed'} size="small" />
        <Text style={[styles.statusText, { color: status.isOpen ? '#2E7D32' : '#C62828' }]}>
          {status.text}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  cardHeader: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 10 },
  iconContainer: { width: 50, height: 50, borderRadius: 25, backgroundColor: '#FFD100', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  shopInfo: { flex: 1 },
  shopName: { fontSize: 17, fontWeight: 'bold', color: '#0C2340', marginBottom: 4 },
  categoryBadge: { alignSelf: 'flex-start', backgroundColor: '#E3F2FD', paddingHorizontal: 10, paddingVertical: 3, borderRadius: 12 },
  categoryText: { fontSize: 11, color: '#1976D2', fontWeight: '600' },
  description: { fontSize: 13, color: '#666', marginBottom: 10, lineHeight: 18 },
  detailsContainer: { marginBottom: 10 },
  detailItem: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 4 },
  detailText: { fontSize: 13, color: '#666' },
  statusContainer: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingTop: 10, borderTopWidth: 1, borderTopColor: '#f0f0f0' },
  statusText: { fontSize: 12, fontWeight: '500' },
});