import React, { useState, useMemo } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import { Shop, Item, CatalogSortOption } from '../../types/shops';
import ItemCard from '../../components/shops/ItemCard';
import FilterBar from '../../components/shops/FilterBar';

interface CatalogViewProps {
  shop: Shop;
  items: Item[];
  onBack: () => void;
  onItemPress: (itemId: string) => void;
}

export default function CatalogView({ shop, items, onBack, onItemPress }: CatalogViewProps) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<CatalogSortOption>('name');

  const categories = useMemo(() => {
    const cats = [...new Set(items.map(item => item.category))];
    return ['All', ...cats];
  }, [items]);

  const categoryFilters = categories.map(cat => ({ id: cat, label: cat }));

  const filteredAndSortedItems = useMemo(() => {
    let result = [...items];
    if (selectedCategory !== 'All') result = result.filter(item => item.category === selectedCategory);
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(item => item.name.toLowerCase().includes(query) || item.description.toLowerCase().includes(query));
    }
    switch (sortBy) {
      case 'name': result.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'price-asc': result.sort((a, b) => a.basePrice - b.basePrice); break;
      case 'price-desc': result.sort((a, b) => b.basePrice - a.basePrice); break;
    }
    return result;
  }, [items, selectedCategory, searchQuery, sortBy]);

  const resetFilters = () => {
    setSelectedCategory('All');
    setSearchQuery('');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <FontAwesome name="arrow-left" size={20} color="#0C2340" />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>{shop.name}</Text>
          <Text style={styles.headerSubtitle}>{items.length} items</Text>
        </View>
        <View style={styles.placeholder} />
      </View>

      <FilterBar
        filters={categoryFilters}
        selectedFilter={selectedCategory}
        onFilterChange={setSelectedCategory}
        showSearch
        searchValue={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Search items..."
      />

      <View style={styles.sortContainer}>
        <Text style={styles.sortLabel}>Sort:</Text>
        {(['name', 'price-asc', 'price-desc'] as CatalogSortOption[]).map(option => (
          <TouchableOpacity key={option} style={[styles.sortOption, sortBy === option && styles.sortOptionActive]} onPress={() => setSortBy(option)}>
            <Text style={[styles.sortOptionText, sortBy === option && styles.sortOptionTextActive]}>
              {option === 'name' ? 'A-Z' : option === 'price-asc' ? 'Price ↑' : 'Price ↓'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView style={styles.list} showsVerticalScrollIndicator={false}>
        {filteredAndSortedItems.length === 0 ? (
          <View style={styles.emptyState}>
            <FontAwesome name="search" size={48} color="#ccc" />
            <Text style={styles.emptyTitle}>No items found</Text>
            <Text style={styles.emptyText}>Try adjusting your search or filters</Text>
            <TouchableOpacity style={styles.resetButton} onPress={resetFilters}>
              <Text style={styles.resetButtonText}>Reset Filters</Text>
            </TouchableOpacity>
          </View>
        ) : (
          filteredAndSortedItems.map(item => (
            <ItemCard key={item.id} item={item} onPress={() => onItemPress(item.id)} />
          ))
        )}
        <View style={styles.bottomPadding} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e0e0e0' },
  backButton: { padding: 8 },
  headerCenter: { flex: 1, alignItems: 'center', marginHorizontal: 8 },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#0C2340' },
  headerSubtitle: { fontSize: 12, color: '#666' },
  placeholder: { width: 36 },
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