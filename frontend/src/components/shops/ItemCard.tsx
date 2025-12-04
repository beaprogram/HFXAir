import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Item } from '../../types/shops';
import { formatPrice } from '../../utils/shopHelpers';
import StatusBadge from './StatusBadge';

interface ItemCardProps {
  item: Item;
  onPress: () => void;
}

export default function ItemCard({ item, onPress }: ItemCardProps) {
  const isAvailable = item.availability !== 'Out of Stock';

  return (
    <TouchableOpacity
      style={[styles.card, !isAvailable && styles.cardDisabled]}
      onPress={onPress}
      activeOpacity={0.7}
      disabled={!isAvailable}
    >
      <View style={styles.imageContainer}>
        <FontAwesome name="shopping-basket" size={28} color="#0C2340" />
      </View>

      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.itemName} numberOfLines={2}>{item.name}</Text>
          <StatusBadge status={item.availability} size="small" />
        </View>

        <Text style={styles.description} numberOfLines={2}>{item.description}</Text>

        <View style={styles.footer}>
          <Text style={styles.price}>{formatPrice(item.basePrice, item.currency)}</Text>
          {item.variantTypes && item.variantTypes.length > 0 && (
            <View style={styles.optionsBadge}>
              <Text style={styles.optionsText}>
                {item.variantTypes.length} option{item.variantTypes.length > 1 ? 's' : ''}
              </Text>
            </View>
          )}
          <FontAwesome name="chevron-right" size={14} color="#ccc" style={styles.chevron} />
        </View>

        {item.availability === 'Low Stock' && (
          <Text style={styles.stockWarning}>Low stock!</Text>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: { flexDirection: 'row', backgroundColor: '#fff', borderRadius: 12, padding: 12, marginBottom: 10, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.08, shadowRadius: 3, elevation: 2 },
  cardDisabled: { opacity: 0.6 },
  imageContainer: { width: 70, height: 70, borderRadius: 10, backgroundColor: '#f5f5f5', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  content: { flex: 1 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4, gap: 8 },
  itemName: { fontSize: 15, fontWeight: '600', color: '#0C2340', flex: 1 },
  description: { fontSize: 12, color: '#666', marginBottom: 8, lineHeight: 16 },
  footer: { flexDirection: 'row', alignItems: 'center' },
  price: { fontSize: 16, fontWeight: 'bold', color: '#0C2340' },
  optionsBadge: { backgroundColor: '#E8F5E9', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10, marginLeft: 10 },
  optionsText: { fontSize: 10, color: '#2E7D32', fontWeight: '600' },
  chevron: { marginLeft: 'auto' },
  stockWarning: { fontSize: 11, color: '#E65100', fontWeight: '500', marginTop: 4 },
});