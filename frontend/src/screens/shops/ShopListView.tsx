import React, { useState, useMemo } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Shop, ShopSortOption } from '../../types/shops';
import { isShopOpen } from '../../utils/shopHelpers';
import ShopCard from '../../components/shops/ShopCard';
import FilterBar from '../../components/shops/FilterBar';

interface ShopListViewProps {
  shops: Shop[];
  onShopPress: (shopId: string) => void;
  onMyBookingsPress: () => void;
  bookingsCount: number;
}

export default function ShopListView({ shops, onShopPress, onMyBookingsPress, bookingsCount }: ShopListViewProps) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [openNowFilter, setOpenNowFilter] = useState(false);
  const [sortBy, setSortBy] = useState<ShopSortOption>('name');

  const categories = useMemo(() => {
    const cats = [...new Set(shops.map(s => s.category))];
    return ['All', ...cats];
  }, [shops]);

  const categoryFilters = categories.map(cat => ({ id: cat, label: cat }));

  const filteredAndSortedShops = useMemo(() => {
    let result = [...shops];
    if (selectedCategory !== 'All') result = result.filter(shop => shop.category === selectedCategory);
    if (openNowFilter) result = result.filter(shop => isShopOpen(shop));
    switch (sortBy) {
      case 'name': result.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'gate': result.sort((a, b) => (a.gate || 'ZZZ').localeCompare(b.gate || 'ZZZ')); break;
      case 'status': result.sort((a, b) => (isShopOpen(a) ? 0 : 1) - (isShopOpen(b) ? 0 : 1)); break;
    }
    return result;
  }, [shops, selectedCategory, openNowFilter, sortBy]);

  const resetFilters = () => { setSelectedCategory('All'); setOpenNowFilter(false); };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Airport Shops</Text>
        <TouchableOpacity style={styles.bookingsButton} onPress={onMyBookingsPress}>
          <FontAwesome name="ticket" size={16} color="#0C2340" />
          <Text style={styles.bookingsText}>My Reservations</Text>
          {bookingsCount > 0 && (
            <View style={styles.badge}><Text style={styles.badgeText}>{bookingsCount}</Text></View>
          )}
        </TouchableOpacity>
      </View>

      <FilterBar
        filters={categoryFilters}
        selectedFilter={selectedCategory}
        onFilterChange={setSelectedCategory}
        showOpenNowToggle
        openNowActive={openNowFilter}
        onOpenNowToggle={() => setOpenNowFilter(!openNowFilter)}
      />

      <View style={styles.sortContainer}>
        <Text style={styles.sortLabel}>Sort by:</Text>
        {(['name', 'gate', 'status'] as ShopSortOption[]).map(option => (
          <TouchableOpacity key={option} style={[styles.sortOption, sortBy === option && styles.sortOptionActive]} onPress={() => setSortBy(option)}>
            <Text style={[styles.sortOptionText, sortBy === option && styles.sortOptionTextActive]}>
              {option === 'name' ? 'A-Z' : option === 'gate' ? 'Gate' : 'Open'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView style={styles.list} showsVerticalScrollIndicator={false}>
        {filteredAndSortedShops.length === 0 ? (
          <View style={styles.emptyState}>
            <FontAwesome name="search" size={48} color="#ccc" />
            <Text style={styles.emptyTitle}>No shops found</Text>
            <Text style={styles.emptyText}>Try adjusting your filters</Text>
            <TouchableOpacity style={styles.resetButton} onPress={resetFilters}>
              <Text style={styles.resetButtonText}>Reset Filters</Text>
            </TouchableOpacity>
          </View>
        ) : (
          filteredAndSortedShops.map(shop => <ShopCard key={shop.id} shop={shop} onPress={() => onShopPress(shop.id)} />)
        )}
        <View style={styles.bottomPadding} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8, backgroundColor: '#fff' },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#0C2340' },
  bookingsButton: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFD100', paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, gap: 6 },
  bookingsText: { fontSize: 13, fontWeight: '600', color: '#0C2340' },
  badge: { backgroundColor: '#0C2340', borderRadius: 10, minWidth: 20, height: 20, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 6 },
  badgeText: { color: '#fff', fontSize: 11, fontWeight: 'bold' },
  sortContainer: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 10, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  sortLabel: { fontSize: 13, color: '#666', marginRight: 12 },
  sortOption: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14, marginRight: 8, backgroundColor: '#f5f5f5' },
  sortOptionActive: { backgroundColor: '#E3F2FD' },
  sortOptionText: { fontSize: 12, color: '#666', fontWeight: '500' },
  sortOptionTextActive: { color: '#1976D2' },
  list: { flex: 1, paddingHorizontal: 16, paddingTop: 12 },
  emptyState: { alignItems: 'center', paddingTop: 60 },
  emptyTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginTop: 16 },
  emptyText: { fontSize: 14, color: '#666', marginTop: 8 },
  resetButton: { marginTop: 20, backgroundColor: '#0C2340', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 24 },
  resetButtonText: { color: '#FFD100', fontWeight: '600', fontSize: 14 },
  bottomPadding: { height: 20 },
});